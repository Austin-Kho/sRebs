from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# --------------------------------------------------------
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from django.db.models import Sum
from rebs_contract.models import Contract
from rebs_notice.models import SalesBillIssue
from rebs_cash.models import SalesPriceByGT, ProjectCashBook, InstallmentPaymentOrder


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'rebs/main/1_1_dashboard.html'

def memu2_1(request):
    return render(request, 'rebs/main/2_1_schedule.html')


class ExportPdfBill(View):
    """고지서 리스트"""

    def get(self, request):
        context = {}
        project = request.GET.get('project')
        context['issue_date'] = request.GET.get('date')
        context['bill'] = SalesBillIssue.objects.get(project_id=project)

        context['pay_orders'] = pay_orders = InstallmentPaymentOrder.objects.filter(project=project)
        now_due_order = context['bill'].now_payment_order.pay_code if context['bill'].now_payment_order else 2
        context['contractor_id'] = contractor_id = request.GET.get('seq').split('-')
        context['data_list'] = []

        for id in contractor_id:

            cont = {}
            cont['contract'] = contract = Contract.objects.get(contractor__id=id) # 해당 계약건

            # 1. 분양가 구하기
            try:
                unit_set = contract.contractunit.unitnumber
            except Exception:
                unit_set = None
            cont['unit'] = unit_set
            group = contract.order_group
            type = contract.contractunit.unit_type
            prices = SalesPriceByGT.objects.filter(project=project, order_group=group, unit_type=type)
            if unit_set:
                floor = contract.contractunit.unitnumber.floor_type
                prices = prices.filter(unit_floor_type=floor)
            this_price = prices.first()
            cont['price'] = this_price if unit_set else "동호 지정 후 고지"
            # --------------------------------------------------------------

            # 2. 완납금액 및 완납회차 구하기
            paid_list = ProjectCashBook.objects.filter(contract=contract).order_by('installment_order', 'deal_date')
            cont['paid_sum'] = paid_sum = paid_list.aggregate(Sum('income'))['income__sum'] # 기 납부총액
            paid_sum = paid_sum if paid_sum else 0 # 기 납부총액(None 이면 0)
            this_amounts = this_price.installmentpaymentamount_set.all()  # 해당 건 전체 약정액
            amount_sum = 0  # 저정회차까지 약정액 합계
            for ta in this_amounts:
                amount_sum += ta.payment_amount    # 저정회차까지 약정액 합계 (+)
                if paid_sum >= amount_sum:         # 기 납부총액이 약정액보다 같거나 큰지 검사 ?????
                    paid_order = ta.payment_order  # 최종 납부회차 구하기
                if ta.payment_order.id == now_due_order: # 순회 회차가 지정회차와 같으면 순회중단
                    break
            cont['paid_amounts'] = this_amounts.filter(payment_order__pay_code__lte=now_due_order)
            payment_by_order = []
            for pa in cont['paid_amounts']:
                payment_by_order.append(paid_list.filter(installment_order=pa.payment_order).aggregate(Sum('income'))['income__sum'])
            cont['payment_by_order'] = list(reversed(payment_by_order))
            paid_amounts = this_amounts.filter(payment_order__pay_code__lte=paid_order.pay_code)
            paid_amount_sum = paid_amounts.aggregate(Sum('payment_amount'))['payment_amount__sum'] # 완납회차까지 약정금
            # --------------------------------------------------------------

            # 3. 미납 회차 (지정회차 - 완납회차)
            cont['second_date'] = contract.contractor.contract_date + timedelta(days=31)
            unpaid_amounts_all = this_amounts.filter(payment_order__pay_code__gt=paid_order.pay_code)
            cont['unpaid_amounts'] = unpaid_amounts = unpaid_amounts_all.filter(payment_order__pay_code__lte=now_due_order) # 지정 회차까지 약정액
            cont['unpaid_amounts_sum'] = unpaid_amounts_sum = unpaid_amounts.aggregate(Sum('payment_amount'))['payment_amount__sum']
            # --------------------------------------------------------------

            # 5. 미납 금액 (약정금액 - 납부금액)
            cont['cal_unpaid'] = cal_unpaid = paid_sum - paid_amount_sum
            cont['cal_unpaid_sum'] = cal_unpaid_sum = unpaid_amounts_sum - cal_unpaid
            cont['arrears'] = 0 # 연체료 - 향후 연체료 계산 변수
            cont['arrears_sum'] = arrears_sum = 0 # 연체료 합계 - 향후 연체료 합계 계산 변수
            cont['cal_due_payment'] = cal_unpaid_sum + arrears_sum
            pm_cost_sum = unpaid_amounts.filter(payment_order__is_pm_cost=True).aggregate(Sum('payment_amount'))['payment_amount__sum']
            cont['pm_cost_sum'] = pm_cost_sum if pm_cost_sum else 0

            # 6. 잔여 약정 목록
            cont['remaining_orders'] = remaining_orders = this_amounts.filter(payment_order__pay_code__gt=now_due_order)
            if not unit_set:
                cont['remaining_orders'] = remaining_orders.filter(payment_order__pay_sort='1')
            cont['modi_dates'] = 0 # 선납 or 지연 일수
            cont['modifi'] = 0 # 선납할인 or 연체 가산금계산
            cont['modifi_sum'] = 0 # 가감액 합계

            num = unpaid_amounts.count() + 1 if cont['pm_cost_sum'] else unpaid_amounts.count()
            rem_blank = 0 if unit_set else remaining_orders.count()
            blank_line = (14 - (num + pay_orders.count())) + rem_blank
            cont['blank_line'] = '*' * blank_line

            context['data_list'].append(cont)

        html_string = render_to_string('pdf/bill_control.html', context)

        html = HTML(string=html_string)
        html.write_pdf(target='/tmp/mypdf.pdf')

        fs = FileSystemStorage('/tmp')
        with fs.open('mypdf.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="payment_bill({len(contractor_id)}).pdf"'
            return response

        return response

