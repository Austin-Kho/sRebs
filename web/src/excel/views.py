##############################################################################
#
# A Django view class to write an Excel file using the XlsxWriter
# module.
#
# Copyright 2013-2020, John McNamara, jmcnamara@cpan.org
#
import io
from django.http import HttpResponse
import xlsxwriter
import xlwt
import xlrd

from datetime import datetime
from django.db.models import Q
from django.views.generic import View

from rebs_company.models import Company
from rebs_project.models import Project, Site, SiteOwner, SiteContract
from rebs_contract.models import Contract, ContractorRelease
from rebs_cash.models import CashBook, ProjectCashBook


TODAY = datetime.today().strftime('%Y-%m-%d')

class ExportContracts(View):
    """계약자 리스트"""

    def get(self, request):

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('계약목록_정보')

        worksheet.set_default_row(20)

        project = Project.objects.get(pk=request.GET.get('project'))
        cols = request.GET.get('col').split('-')

        # 1. Title
        row_num = 0
        title_format = workbook.add_format()
        worksheet.set_row(row_num, 50)
        title_format.set_font_size(18)
        title_format.set_align('vcenter')
        title_format.set_bold()
        worksheet.merge_range(row_num, 0, row_num, len(cols), str(project) + ' 계약자 리스트', title_format)

        # 2. Header
        row_num = 1
        worksheet.set_row(row_num, 18)
        worksheet.write(row_num, len(cols), TODAY + ' 현재', workbook.add_format({'align': 'right'}))

        # 3. Header
        row_num = 2
        worksheet.set_row(row_num, 25, workbook.add_format({'bold': True}))

        # title_list
        data_source = [[],
                 ['일련번호', 'serial_number', 10],
                 ['인가여부', 'contractor__is_registed', 8],
                 ['차수', 'order_group__order_group_name', 10],
                 ['타입', 'contractunit__unit_type__name', 7],
                 ['동', 'contractunit__unitnumber__bldg_no', 7],
                 ['호수', 'contractunit__unitnumber__bldg_unit_no', 7],
                 ['계약자', 'contractor__name', 10],
                 ['생년월일', 'contractor__birth_date', 12],
                 ['계약일자', 'contractor__contract_date', 12],
                 ['연락처[1]', 'contractor__contractorcontact__cell_phone', 14],
                 ['연락처[2]', 'contractor__contractorcontact__home_phone', 14],
                 ['연락처[3]', 'contractor__contractorcontact__other_phone', 14],
                 ['이메일', 'contractor__contractorcontact__email', 15],
                 ['주소[등본]', 'contractor__contractoraddress__id_zipcode', 7],
                 ['', 'contractor__contractoraddress__id_address1', 35],
                 ['', 'contractor__contractoraddress__id_address2', 20],
                 ['', 'contractor__contractoraddress__id_address3', 40],
                 ['주소[우편]', 'contractor__contractoraddress__dm_zipcode', 7],
                 ['', 'contractor__contractoraddress__dm_address1', 35],
                 ['', 'contractor__contractoraddress__dm_address2', 20],
                 ['', 'contractor__contractoraddress__dm_address3', 40],
                 ['비고', 'contractor__note', 45]]

        titles = ['No']
        params = []
        widths = [7]

        for i in cols:
            titles.append(data_source[int(i)][0])
            params.append(data_source[int(i)][1])
            widths.append(data_source[int(i)][2])

        h_format = workbook.add_format()
        h_format.set_bold()
        h_format.set_border()
        h_format.set_align('center')
        h_format.set_align('vcenter')
        h_format.set_bg_color('#eeeeee')

        # Adjust the column width.
        for i, cw in enumerate(widths):
            worksheet.set_column(i, i, cw)

        # Write header
        for col_num, col in enumerate(titles):
            if '주소' in col:
                worksheet.merge_range(row_num, col_num, row_num, col_num + 3, titles[col_num], h_format)
            else:
                worksheet.write(row_num, col_num, titles[col_num], h_format)

        # 4. Body
        # Get some data to write to the spreadsheet.
        data = Contract.objects.filter(project=project,
                                       contractunit__contract__isnull=False,
                                       contractor__status='2').order_by('contractor__contract_date')
        if request.GET.get('group'):
            data = data.filter(order_group=request.GET.get('group'))
        if request.GET.get('type'):
            data = data.filter(contractunit__unit_type=request.GET.get('type'))
        if self.request.GET.get('dong'):
            data = data.filter(contractunit__unitnumber__bldg_no=self.request.GET.get('dong'))
        if request.GET.get('status'):
            data = data.filter(contractor__status=request.GET.get('status'))
        if request.GET.get('reg'):
            result = True if request.GET.get('reg') == '1' else False
            data = data.filter(contractor__is_registed=result)
        order_list = ['-created_at', 'created_at', '-contractor__contract_date',
                      'contractor__contract_date', '-serial_number',
                      'serial_number', '-contractor__name', 'contractor__name']
        if self.request.GET.get('order'):
            data = data.order_by(order_list[int(self.request.GET.get('order'))])
        if request.GET.get('sdate'):
            data = data.filter(contractor__contract_date__gte=request.GET.get('sdate'))
        if request.GET.get('edate'):
            data = data.filter(contractor__contract_date__lte=request.GET.get('edate'))
        if request.GET.get('q'):
            data = data.filter(
                Q(serial_number__icontains=request.GET.get('q')) |
                Q(contractor__name__icontains=request.GET.get('q')) |
                Q(contractor__note__icontains=request.GET.get('q')))

        data = data.values_list(*params)

        b_format = workbook.add_format()
        b_format.set_align('vcenter')
        b_format.set_border()
        b_format.set_num_format('yyyy-mm-dd')
        b_format.set_align('center')

        body_format = {
            'border': True,
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd',
            'align': 'center',
        }

        is_reg = []  # ('인가여부',)
        is_date = []  # ('생년월일', '계약일자')
        reg_data = ('미인가', '인가')
        is_left = []

        # Write body
        for col_num, col in enumerate(titles):
            if col == '인가여부':
                is_reg.append(col_num)
            if col in ('생년월일', '계약일자'):
                is_date.append(col_num)
            if col in ('', '비고'):
               is_left.append(col_num)

        for i, row in enumerate(data):
            row = list(row)
            row_num += 1
            row.insert(0, i + 1)
            for col_num, cell_data in enumerate(row):
                if col_num == 0:
                    body_format['num_format'] = '#,##0'
                else:
                    body_format['num_format'] = 'yyyy-mm-dd'
                if col_num in is_reg: # 인가 여부 데이터 치환
                    cell_data = reg_data[int(cell_data)]
                if col_num in is_left:
                    if 'align' in body_format:
                        del body_format['align']
                else:
                    if 'align' not in body_format:
                        body_format['align'] = 'center'
                bf = workbook.add_format(body_format)
                worksheet.write(row_num, col_num, cell_data, bf)


        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = '{date}-contracts.xlsx'.format(date=datetime.now().strftime('%Y-%m-%d'))
        file_format = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(output, content_type=file_format)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


class ExportApplicants(View):
    """청약자 리스트"""

    def get(self, request):

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('청약목록_정보')

        worksheet.set_default_row(20)

        project = Project.objects.get(pk=request.GET.get('project'))

        # title_list
        data_source = [[],
                       ['일련번호', 'serial_number', 10],
                       ['차수', 'order_group__order_group_name', 10],
                       ['타입', 'contractunit__unit_type__name', 7],
                       ['청약자', 'contractor__name', 10],
                       ['청약일자', 'contractor__reservation_date', 12],
                       ['연락처[1]', 'contractor__contractorcontact__cell_phone', 14],
                       ['연락처[2]', 'contractor__contractorcontact__home_phone', 14],
                       ['연락처[3]', 'contractor__contractorcontact__other_phone', 14],
                       ['이메일', 'contractor__contractorcontact__email', 15],
                       ['비고', 'contractor__note', 45]]

        if project.is_unit_set:
            data_source.append(
                ['동', 'contractunit__unitnumber__bldg_no', 7],
                ['호수', 'contractunit__unitnumber__bldg_unit_no', 7]
            )

        # 1. Title
        row_num = 0
        worksheet.set_row(row_num, 50)
        title_format = workbook.add_format()
        title_format.set_bold()
        title_format.set_font_size(18)
        title_format.set_align('vcenter')
        worksheet.merge_range(row_num, 0, row_num, len(data_source) - 1, str(project) + ' 청약자 리스트', title_format)

        # 2. Pre Header - Date
        row_num = 1
        worksheet.set_row(row_num, 18)
        worksheet.write(row_num, len(data_source) - 1, TODAY + ' 현재', workbook.add_format({'align': 'right'}))

        # 3. Header
        row_num = 2
        worksheet.set_row(row_num, 25, workbook.add_format({'bold': True}))

        titles = ['No'] # header titles
        params = [] # ORM 추출 field
        widths = [7] # No. 컬럼 넓이

        for ds in data_source:
            if ds:
                titles.append(ds[0])
                params.append(ds[1])
                widths.append(ds[2])

        h_format = workbook.add_format()
        h_format.set_bold()
        h_format.set_border()
        h_format.set_align('center')
        h_format.set_align('vcenter')
        h_format.set_bg_color('#eeeeee')

        # Adjust the column width.
        for i, col_width in enumerate(widths):
            worksheet.set_column(i, i, col_width)

        # Write header
        for col_num, col in enumerate(titles):
            worksheet.write(row_num, col_num, titles[col_num], h_format)

        # 4. Body
        # Get some data to write to the spreadsheet.
        data = Contract.objects.filter(project=project,
                                              contractunit__contract__isnull=False,
                                              contractor__status='1')

        data = data.values_list(*params)

        b_format = workbook.add_format()
        b_format.set_border()
        b_format.set_align('center')
        b_format.set_align('vcenter')
        b_format.set_num_format('yyyy-mm-dd')

        body_format = {
            'border': True,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        }

        is_left = []
        # Write header
        for col_num, col in enumerate(titles):
            if col in ('비고'):
                is_left.append(col_num)

        # Write header
        for i, row in enumerate(data):
            row = list(row)
            row_num += 1
            row.insert(0, i + 1)
            for col_num, cell_data in enumerate(row):
                if col_num == 0:
                    body_format['num_format'] = '#,##0'
                else:
                    body_format['num_format'] = 'yyyy-mm-dd'
                if col_num in is_left:
                    if 'align' in body_format:
                        del body_format['align']
                else:
                    if 'align' not in body_format:
                        body_format['align'] = 'center'
                bformat = workbook.add_format(body_format)
                worksheet.write(row_num, col_num, cell_data, bformat)

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = '{date}-applicants.xlsx'.format(date=datetime.now().strftime('%Y-%m-%d'))
        file_format = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(output, content_type=file_format)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


class ExportReleases(View):
    """해지자 리스트"""

    def get(self, request):

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('해지자목록_정보')

        worksheet.set_default_row(20)

        project = Project.objects.get(pk=request.GET.get('project'))

        # title_list
        data_source = [[],
                       ['해지자', 'contractor__name', 10],
                       ['해지일련번호', 'contractor__contract__serial_number', 30],
                       ['현재상태', 'status', 12],
                       ['환불(예정)금액', 'refund_amount', 15],
                       ['은행', 'refund_account_bank', 15],
                       ['계좌번호', 'refund_account_number', 18],
                       ['예금주', 'refund_account_depositor', 12],
                       ['해지신청일', 'request_date', 14],
                       ['환불처리일', 'completion_date', 14],
                       ['비고', 'note', 45]]

        # 1. Title
        row_num = 0
        worksheet.set_row(row_num, 50)
        title_format = workbook.add_format()
        title_format.set_bold()
        title_format.set_font_size(18)
        title_format.set_align('vcenter')
        worksheet.merge_range(row_num, 0, row_num, len(data_source) - 1, str(project) + ' 해지자 리스트', title_format)

        # 2. Pre Header - Date
        row_num = 1
        worksheet.set_row(row_num, 18)
        worksheet.write(row_num, len(data_source) - 1, TODAY + ' 현재', workbook.add_format({'align': 'right'}))

        # 3. Header - 1
        row_num = 2
        worksheet.set_row(row_num, 20, workbook.add_format({'bold': True}))

        titles = ['No'] # header titles
        params = [] # ORM 추출 field
        widths = [7] # No. 컬럼 넓이

        for ds in data_source:
            if ds:
                titles.append(ds[0])
                params.append(ds[1])
                widths.append(ds[2])

        h_format = workbook.add_format()
        h_format.set_bold()
        h_format.set_border()
        h_format.set_align('center')
        h_format.set_align('vcenter')
        h_format.set_bg_color('#eeeeee')

        # Adjust the column width.
        for i, col_width in enumerate(widths):
            worksheet.set_column(i, i, col_width)

        # Write header - 1
        for col_num, title in enumerate(titles):
            if col_num == 5:
                worksheet.merge_range(row_num, col_num, row_num, col_num + 2, '환불 계좌', h_format)
            elif col_num in [6, 7]:
                pass
            else:
                worksheet.write(row_num, col_num, title, h_format)

        # Write Header - 2
        row_num = 3
        for col_num, title in enumerate(titles):
            if col_num in [5, 6, 7]:
                worksheet.write(row_num, col_num, title, h_format)
            else:
                worksheet.merge_range(row_num - 1, col_num, row_num, col_num, title, h_format)

        # 4. Body
        # Get some data to write to the spreadsheet.
        data = ContractorRelease.objects.filter(project=project)

        data = data.values_list(*params)

        b_format = workbook.add_format()
        b_format.set_border()
        b_format.set_align('center')
        b_format.set_align('vcenter')
        b_format.set_num_format('yyyy-mm-dd')

        body_format = {
            'border': True,
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd'
        }

        # Write header
        for i, row in enumerate(data):
            row = list(row)
            row_num += 1
            row.insert(0, i + 1)
            for col_num, cell_data in enumerate(row):
                if col_num in [0, 4]:
                    body_format['num_format'] = '#,##0'
                else:
                    body_format['num_format'] = 'yyyy-mm-dd'
                if col_num == 4:
                    body_format['align'] = 'right'
                elif col_num == 10:
                    body_format['align'] = 'left'
                else:
                    body_format['align'] = 'center'
                if col_num == 3:
                    cell_data = {'3': '신청 중', '4': '처리완료'}[cell_data]
                bformat = workbook.add_format(body_format)
                worksheet.write(row_num, col_num, cell_data, bformat)

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = '{date}-releases.xlsx'.format(date=datetime.now().strftime('%Y-%m-%d'))
        file_format = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(output, content_type=file_format)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


def export_cont_dashboard_xls(request):
    """동호수표"""
    pass


def export_payments_xls(request):
    """분양대금 수납 내역"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={date}-payments.xls'.format(
        date=datetime.now().strftime('%Y-%m-%d'))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('분양대금납부_내역')  # 시트 이름

    # get_data: ?project=1&sd=2020-12-01&ed=2020-12-02&ipo=4&ba=5&up=on&q=#
    project = Project.objects.get(pk=request.GET.get('project'))
    sd = request.GET.get('sd')
    ed = request.GET.get('ed')
    ipo = request.GET.get('ipo')
    ba = request.GET.get('ba')
    up = request.GET.get('up')
    q = request.GET.get('q')

    today = TODAY
    sd = sd if sd else '1900-01-01'
    ed = ed if ed else today
    obj_list = ProjectCashBook.objects.filter(project=project, project_account_d2__in=(1, 2), deal_date__range=(sd, ed)).order_by('-deal_date', '-created_at')

    if ipo:
        obj_list = obj_list.filter(installment_order_id=ipo)

    if ba:
        obj_list = obj_list.filter(bank_account__id=ba)

    if up:
        obj_list = obj_list.filter(
            (Q(is_contract_payment=False) | Q(contract__isnull=True)) &
            (Q(project_account_d1_id__in=(1, 2)) | Q(project_account_d2_id__in=(1, 2)))
        )

    if q:
        obj_list = obj_list.filter(
            Q(contract__contractor__name__icontains=q) |
            Q(trader__icontains=q) |
            Q(content__icontains=q) |
            Q(note__icontains=q))

    # Sheet Title, first row
    row_num = 0

    style = xlwt.XFStyle()
    style.font.bold = True
    style.font.height = 300
    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬

    ws.write(row_num, 0, str(project) + ' 계약자 대금 납부내역', style)
    ws.row(0).height_mismatch = True
    ws.row(0).height = 38 * 20

    # title_list

    resources = [
        ['거래일자', 'deal_date'],
        ['차수', 'contract__order_group__order_group_name'],
        ['타입', 'contract__contractunit__unit_type__name'],
        ['일련번호', 'contract__serial_number'],
        ['계약자', 'contract__contractor__name'],
        ['입금 금액', 'income'],
        ['납입회차', 'installment_order__pay_name'],
        ['수납계좌', 'bank_account__alias_name'],
        ['입금자', 'trader']
    ]

    columns = []
    params = []

    for rsc in resources:
        columns.append(rsc[0])
        params.append(rsc[1])

    rows = obj_list.values_list(*params)

    # Sheet header, second row
    row_num = 1

    style = xlwt.XFStyle()
    style.font.bold = True

    # 테두리 설정
    # 가는 실선 : 1, 작은 굵은 실선 : 2,가는 파선 : 3, 중간가는 파선 : 4, 큰 굵은 실선 : 5, 이중선 : 6,가는 점선 : 7
    # 큰 굵은 점선 : 8,가는 점선 : 9, 굵은 점선 : 10,가는 이중 점선 : 11, 굵은 이중 점선 : 12, 사선 점선 : 13
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style.pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style)

    # Sheet body, remaining rows
    style = xlwt.XFStyle()
    # 테두리 설정
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    # style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for row in rows:
        row_num += 1
        for col_num, col in enumerate((columns)):
            row = list(row)

            if col_num == 0:
                style.num_format_str = 'yyyy-mm-dd'
                ws.col(col_num).width = 110 * 30

            if '금액' in col:
                style.num_format_str = '#,##'
                ws.col(col_num).width = 110 * 30

            if col == '차수' or col == '납입회차' or col == '일련번호':
                ws.col(col_num).width = 110 * 30

            if col == '수납계좌':
                ws.col(col_num).width = 170 * 30

            if col == '입금자' or col == '계약자':
                ws.col(col_num).width = 110 * 30

            ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response


def export_project_balance_xls(request):
    """프로젝트 계좌별 잔고 내역"""
    pass


def export_project_daily_cash_xls(request):
    """프로젝트 일별 입출금 내역"""
    pass


def export_budget_xls(request):
    """프로젝트 예산대비 현황"""
    pass


def export_project_cash_xls(request):
    """프로젝트별 입출금 내역"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={date}-project-cashbook.xls'.format(
        date=datetime.now().strftime('%Y-%m-%d'))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('프로젝트_입출금_내역')  # 시트 이름

    # get_data: ?project=1&sdate=2020-12-01&edate=2020-12-31&sort=1&d1=1&d2=1&bank_acc=5&q=ㅁ
    project = Project.objects.get(pk=request.GET.get('project'))
    sdate = request.GET.get('sdate')
    edate = request.GET.get('edate')
    sort = request.GET.get('sort')
    d1 = request.GET.get('d1')
    d2 = request.GET.get('d2')
    bank_acc = request.GET.get('bank_acc')
    q = request.GET.get('q')

    today = TODAY
    sdate = sdate if sdate else '1900-01-01'
    edate = edate if edate else today
    obj_list = ProjectCashBook.objects.filter(project=project, deal_date__range=(sdate, edate)).order_by('-deal_date', '-created_at')

    if sort:
        obj_list = obj_list.filter(cash_category1__icontains=sort)

    if d1:
        obj_list = obj_list.filter(project_account_d1__id=d1)

    if d2:
        obj_list = obj_list.filter(project_account_d2__id=d2)

    if bank_acc:
        obj_list = obj_list.filter(bank_account__id=bank_acc)

    if q:
        obj_list = obj_list.filter(Q(content__icontains=q) | Q(trader__icontains=q))

    # Sheet Title, first row
    row_num = 0

    style = xlwt.XFStyle()
    style.font.bold = True
    style.font.height = 300
    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬

    ws.write(row_num, 0, str(project) + ' 입출금 내역', style)
    ws.row(0).height_mismatch = True
    ws.row(0).height = 38 * 20

    # title_list

    resources = [
         ['거래일자', 'deal_date'],
         ['구분', 'cash_category1'],
         ['현장 계정', 'project_account_d1__name'],
         ['현장 세부계정', 'project_account_d2__name'],
         ['적요', 'content'],
         ['거래처', 'trader'],
         ['거래 계좌', 'bank_account__alias_name'],
         ['입금 금액', 'income'],
         ['출금 금액', 'outlay'],
         ['증빙 자료', 'evidence'],
         ['비고', 'note']]

    columns = []
    params = []

    for rsc in resources:
        columns.append(rsc[0])
        params.append(rsc[1])

    rows = obj_list.values_list(*params)

    # Sheet header, second row
    row_num = 1

    style = xlwt.XFStyle()
    style.font.bold = True

    # 테두리 설정
    # 가는 실선 : 1, 작은 굵은 실선 : 2,가는 파선 : 3, 중간가는 파선 : 4, 큰 굵은 실선 : 5, 이중선 : 6,가는 점선 : 7
    # 큰 굵은 점선 : 8,가는 점선 : 9, 굵은 점선 : 10,가는 이중 점선 : 11, 굵은 이중 점선 : 12, 사선 점선 : 13
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style.pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style)

    # Sheet body, remaining rows
    style = xlwt.XFStyle()
    # 테두리 설정
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    # style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for row in rows:
        row_num += 1
        for col_num, col in enumerate((columns)):
            row = list(row)

            if col == '거래일자':
                style.num_format_str = 'yyyy-mm-dd'
                ws.col(col_num).width = 110 * 30

            if col == '구분':
                if row[col_num] == '1':
                    row[col_num] = '입금'
                if row[col_num] == '2':
                    row[col_num] = '출금'
                if row[col_num] == '3':
                    row[col_num] = '대체'

            if col == '현장 계정':
                ws.col(col_num).width = 110 * 30

            if col == '현장 세부계정':
                ws.col(col_num).width = 160 * 30

            if col == '적요' or col == '거래처':
                ws.col(col_num).width = 180 * 30

            if col == '거래 계좌':
                ws.col(col_num).width = 170 * 30

            if '금액' in col:
                style.num_format_str = '#,##'
                ws.col(col_num).width = 110 * 30

            if col == '증빙 자료':
                if row[col_num] == '0':
                    row[col_num] = '증빙 없음'
                if row[col_num] == '1':
                    row[col_num] = '세금계산서'
                if row[col_num] == '2':
                    row[col_num] = '계산서(면세)'
                if row[col_num] == '3':
                    row[col_num] = '신용카드전표'
                if row[col_num] == '4':
                    row[col_num] = '현금영수증'
                if row[col_num] == '5':
                    row[col_num] = '간이영수증'
                ws.col(col_num).width = 100 * 30

            if col == '비고':
                ws.col(col_num).width = 256 * 30

            ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response


def export_sites_xls(request):
    """프로젝트 지번별 토지목록"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={date}-sites.xls'.format(
        date=datetime.now().strftime('%Y-%m-%d'))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('지번별_토지목록')  # 시트 이름

    # get_data: ?project=1
    project = Project.objects.get(pk=request.GET.get('project'))
    obj_list = Site.objects.filter(project=project)

    # Sheet Title, first row
    # -----------------------
    row_num = 0

    style = xlwt.XFStyle()
    style.font.bold = True
    style.font.height = 300
    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    ws.write(row_num, 0, str(project) + ' 토지목록 조서', style)
    rc = 7 if project.is_returned_area else 5
    ws.merge(0, 0, 0, rc)
    ws.row(0).height_mismatch = True
    ws.row(0).height = 38 * 20
    # -----------------------

    # Sheet space, second row
    # -----------------------
    row_num = 1

    style = xlwt.XFStyle()
    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    style.alignment.horz = style.alignment.HORZ_RIGHT  # 수평정렬
    ws.write(row_num, 7, TODAY + ' 현재', style)
    # -----------------------

    # title_list
    resources = [
        ['No', 'order'],
        ['행정동', 'district'],
        ['지번', 'lot_number'],
        ['지목', 'site_purpose'],
        ['대지면적', 'official_area'],
    ]

    if project.is_returned_area:
        resources.append(['환지면적', 'returned_area'])

    columns = []
    params = []

    for rsc in resources:
        columns.append(rsc[0])
        params.append(rsc[1])

    rows = obj_list.values_list(*params)

    # Sheet header, second row - 1
    # -----------------------
    row_num = 2

    style = xlwt.XFStyle()
    style.font.bold = True

    # 테두리 설정
    # 가는 실선 : 1, 작은 굵은 실선 : 2,가는 파선 : 3, 중간가는 파선 : 4, 큰 굵은 실선 : 5, 이중선 : 6,가는 점선 : 7
    # 큰 굵은 점선 : 8,가는 점선 : 9, 굵은 점선 : 10,가는 이중 점선 : 11, 굵은 이중 점선 : 12, 사선 점선 : 13
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style.pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for col_num, col in enumerate(columns):
        if '면적' in col:
            columns.insert(col_num + 1, '(평)')
        ws.write(row_num, col_num, columns[col_num], style)
    # -----------------------

    # Sheet body, remaining rows
    style = xlwt.XFStyle()
    # 테두리 설정
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    # style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for row in rows:
        row_num += 1
        for col_num, col in enumerate((columns)):
            row = list(row)

            if '면적' in col:
                row.insert(col_num + 1, float(row[col_num])*0.3025)

            ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response


def export_sitesByOwner_xls(request):
    """프로젝트 소유자별 토지목록"""
    pass


def export_sitesContracts_xls(request):
    """프로젝트 토지 계약현황"""
    pass


def export_cash_balance_xls(request):
    """본사 계좌별 잔고 내역"""
    pass


def export_daily_cash_xls(request):
    """본사 일별 입출금 내역"""
    pass


def export_cashbook_xls(request):
    """본사 입출금 내역"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={date}-cashbook.xls'.format(
        date=datetime.now().strftime('%Y-%m-%d'))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('본사_입출금_내역')  # 시트 이름

    # get_data: ?s_date=2018-06-30&e_date=&category1=&category2=&bank_account=&search_word=
    s_date = request.GET.get('s_date')
    e_date = request.GET.get('e_date')
    category1 = request.GET.get('category1')
    category2 = request.GET.get('category2')
    bank_account = request.GET.get('bank_account')
    search_word = request.GET.get('search_word')

    company = Company.objects.first()
    today = TODAY
    s_date = s_date if s_date else '1900-01-01'
    e_date = e_date if e_date else today

    obj_list = CashBook.objects.filter(company=company, deal_date__range=(s_date, e_date))

    if category1:
        obj_list = obj_list.filter(cash_category1__icontains=category1)

    if category2:
        obj_list = obj_list.filter(cash_category2__icontains=category2)

    if bank_account:
        obj_list = obj_list.filter(bank_account__id=bank_account)

    if search_word:
        obj_list = obj_list.filter(
            Q(account__name__icontains=search_word) |
            Q(content__icontains=search_word) |
            Q(trader__icontains=search_word))

    # Sheet Title, first row
    row_num = 0

    style = xlwt.XFStyle()
    style.font.bold = True
    style.font.height = 300
    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬

    ws.write(row_num, 0, str(company) + ' 입출금 내역', style)
    ws.row(0).height_mismatch = True
    ws.row(0).height = 38 * 20

    # title_list

    resources = [
         ['거래일자', 'deal_date'],
         ['구분', 'cash_category1'],
         ['계정', 'cash_category1'],
         ['세부계정', 'account__name'],
         ['적요', 'content'],
         ['거래처', 'trader'],
         ['거래계좌', 'bank_account__alias_name'],
         ['입금금액', 'income'],
         ['출금금액', 'outlay'],
         ['증빙 자료', 'evidence'],
         ['비고', 'note']]

    columns = []
    params = []

    for rsc in resources:
        columns.append(rsc[0])
        params.append(rsc[1])

    rows = obj_list.values_list(*params)

    # Sheet header, second row
    row_num = 1

    style = xlwt.XFStyle()
    style.font.bold = True

    # 테두리 설정
    # 가는 실선 : 1, 작은 굵은 실선 : 2,가는 파선 : 3, 중간가는 파선 : 4, 큰 굵은 실선 : 5, 이중선 : 6,가는 점선 : 7
    # 큰 굵은 점선 : 8,가는 점선 : 9, 굵은 점선 : 10,가는 이중 점선 : 11, 굵은 이중 점선 : 12, 사선 점선 : 13
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style.pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style)

    # Sheet body, remaining rows
    style = xlwt.XFStyle()
    # 테두리 설정
    style.borders.left = 1
    style.borders.right = 1
    style.borders.top = 1
    style.borders.bottom = 1

    style.alignment.vert = style.alignment.VERT_CENTER  # 수직정렬
    # style.alignment.horz = style.alignment.HORZ_CENTER  # 수평정렬

    for row in rows:
        row_num += 1
        for col_num, col in enumerate((columns)):
            row = list(row)

            if col == '거래일자':
                style.num_format_str = 'yyyy-mm-dd'
                ws.col(col_num).width = 110 * 30

            if col == '구분':
                if row[col_num] == '1':
                    row[col_num] = '입금'
                if row[col_num] == '2':
                    row[col_num] = '출금'
                if row[col_num] == '3':
                    row[col_num] = '대체'

            if col == '계정':
                if row[col_num] == '1':
                    row[col_num] = '자산'
                if row[col_num] == '2':
                    row[col_num] = '부채'
                if row[col_num] == '3':
                    row[col_num] = '자본'
                if row[col_num] == '4':
                    row[col_num] = '수익'
                if row[col_num] == '5':
                    row[col_num] = '비용'
                if row[col_num] == '6':
                    row[col_num] = '대체'

            if col == '현장 계정':
                ws.col(col_num).width = 110 * 30

            if col == '세부계정':
                ws.col(col_num).width = 160 * 30

            if col == '적요' or col == '거래처':
                ws.col(col_num).width = 180 * 30

            if col == '거래계좌':
                ws.col(col_num).width = 170 * 30

            if '금액' in col:
                style.num_format_str = '#,##'
                ws.col(col_num).width = 110 * 30

            if col == '증빙자료':
                if row[col_num] == '0':
                    row[col_num] = '증빙 없음'
                if row[col_num] == '1':
                    row[col_num] = '세금계산서'
                if row[col_num] == '2':
                    row[col_num] = '계산서(면세)'
                if row[col_num] == '3':
                    row[col_num] = '신용카드전표'
                if row[col_num] == '4':
                    row[col_num] = '현금영수증'
                if row[col_num] == '5':
                    row[col_num] = '간이영수증'
                ws.col(col_num).width = 100 * 30

            if col == '비고':
                ws.col(col_num).width = 256 * 30

            ws.write(row_num, col_num, row[col_num], style)

    wb.save(response)
    return response
