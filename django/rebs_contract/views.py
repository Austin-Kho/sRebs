from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, Max
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, FormView, TemplateView

from .models import (OrderGroup, Contract, Contractor,
                     ContractorAddress, ContractorContact, ContractorRelease)
from rebs.models import ProjectAccountD1, ProjectAccountD2
from rebs_project.models import Project, UnitType, ContractUnit, UnitNumber
from rebs_cash.models import ProjectBankAccount, ProjectCashBook, InstallmentPaymentOrder

from .forms import ContractRegisterForm, ContractPaymentForm, ContractorReleaseForm


class ContractLV(LoginRequiredMixin, ListView):

    model = Contract

    def get_paginate_by(self, queryset):
        return self.request.GET.get('limit') if self.request.GET.get('limit') else 15

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_queryset(self):
        project = self.get_project()
        contract = Contract.objects.filter(project=project, contractunit__contract__isnull=False,
                                           contractor__status='2').order_by('-created_at')
        if self.request.GET.get('group'):
            contract = contract.filter(order_group=self.request.GET.get('group'))
        if self.request.GET.get('type'):
            contract = contract.filter(contractunit__unit_type=self.request.GET.get('type'))
        if self.request.GET.get('dong'):
            contract = contract.filter(contractunit__unitnumber__bldg_no=self.request.GET.get('dong'))
        if self.request.GET.get('status'):
            contract = contract.filter(contractor__status=self.request.GET.get('status'))
        if self.request.GET.get('register'):
            result = True if self.request.GET.get('register') == '1' else False
            contract = contract.filter(contractor__is_registed=result)
        order_list = ['-created_at', 'created_at', '-contractor__contract_date',
                      'contractor__contract_date', '-serial_number',
                      'serial_number', '-contractor__name', 'contractor__name']
        if self.request.GET.get('order'):
            contract = contract.order_by(order_list[int(self.request.GET.get('order'))])
        if self.request.GET.get('sdate'):
            contract = contract.filter(contractor__contract_date__gte=self.request.GET.get('sdate'))
        if self.request.GET.get('edate'):
            contract = contract.filter(contractor__contract_date__lte=self.request.GET.get('edate'))
        if self.request.GET.get('q'):
            q = self.request.GET.get('q')
            contract = contract.filter(Q(serial_number__icontains=q) |
                                       Q(contractor__name__icontains=q) |
                                       Q(contractor__note__icontains=q))
        return contract

    def get_context_data(self, **kwargs):
        context = super(ContractLV, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['groups'] = OrderGroup.objects.filter(project=self.get_project())
        context['types'] = UnitType.objects.filter(project=self.get_project())
        context['dongs'] = UnitNumber.objects.filter(project=self.get_project()).values('bldg_no').distinct()

        unit_num = []  # 타입별 세대수
        reserv_num = []  # 타입별 청약건
        contract_num = []

        context['total_unit_num'] = 0
        context['total_reserv_num'] = 0
        tcn = []
        ocn = []

        for i, type in enumerate(context['types']):
            units = ContractUnit.objects.filter(unit_type=type).count()  # 타입별 세대수
            reservs = Contractor.objects.filter(contract__project=self.get_project(),
                                                contract__contractunit__unit_type=type,
                                                status='1').count()
            unit_num.append(units)  # 타입별 세대수
            reserv_num.append(reservs)  # 타입별 청약건
            context['total_unit_num'] += unit_num[i]
            context['total_reserv_num'] += reserv_num[i]
            cnum = []
            ocn = []
            for j, og in enumerate(context['groups']):
                cnum.append(Contract.objects.filter(project=self.get_project(),
                                                    contractunit__unit_type=type,
                                                    order_group=og).count())
                ocn.append(Contract.objects.filter(project=self.get_project(),
                                                   order_group=og).count())

            contract_num.append(list(reversed(cnum)))
            tcn.append(sum(cnum))

        context['unit_num'] = list(reversed(unit_num))
        context['reserv_num'] = list(reversed(reserv_num))
        context['contract_num'] = list(reversed(contract_num))
        context['tcn'] = list(reversed(tcn))
        context['ocn'] = list(reversed(ocn))
        context['total_tcn'] = sum(tcn)

        context['reservation_list'] = Contract.objects.filter(project=self.get_project(),
                                                              contractor__status=1)
        context['contract_count'] = self.get_queryset().count()
        return context


class ContractRegisterView(LoginRequiredMixin, FormView):

    form_class = ContractRegisterForm
    template_name = 'rebs_contract/contract_form.html'
    PaymentInlineFormSet = forms.models.inlineformset_factory(
        Contract,
        ProjectCashBook,
        form=ContractPaymentForm,
        extra=0
    )

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_back_url(self):
        page = self.request.GET.get('p')
        limit = self.request.GET.get('l')
        group = self.request.GET.get('g')
        type = self.request.GET.get('t')
        dong = self.request.GET.get('d')
        status = self.request.GET.get('s')
        register = self.request.GET.get('r')
        order = self.request.GET.get('o')
        sdate = self.request.GET.get('sd')
        edate = self.request.GET.get('ed')
        q = self.request.GET.get('q')

        project_str = 'project=' + str(self.get_project().id)
        query_str = '?page=' + page + '&' + project_str if page else '?' + project_str
        query_str = query_str + '&limit=' + limit if limit else query_str
        query_str = query_str + '&group=' + group if group else query_str
        query_str = query_str + '&type=' + type if type else query_str
        query_str = query_str + '&dong=' + dong if dong else query_str
        query_str = query_str + '&status=' + status if status else query_str
        query_str = query_str + '&register=' + register if register else query_str
        query_str = query_str + '&order=' + order if order else query_str
        query_str = query_str + '&sdate=' + sdate if sdate else query_str
        query_str = query_str + '&edate=' + edate if edate else query_str
        query_str = query_str + '&q=' + q if q else query_str
        return reverse_lazy('rebs:contract:index') + query_str

    def get_form(self, form_class=None):
        initial = {
            'project': self.get_project().pk if self.get_project() else None,
            'task': self.request.GET.get('task'),
            'order_group': self.request.GET.get('order_group'),
            'type': self.request.GET.get('type'),
            'contract_unit': self.request.GET.get('contract_unit'),
            'unit_number': self.request.GET.get('unit_number'),
            'back_url': self.get_back_url(),
        }
        if self.request.GET.get('cont_id'):
            contractor = Contractor.objects.get(contract=Contract.objects.get(pk=self.request.GET.get('cont_id')))
            contact = ContractorContact.objects.get(contractor=contractor)
            address = ContractorAddress.objects.get(contractor=contractor)
            initial['name'] = contractor.name
            initial['birth_date'] = contractor.birth_date
            initial['gender'] = contractor.gender
            initial['is_registed'] = contractor.is_registed
            initial['reservation_date'] = contractor.reservation_date
            initial['contract_date'] = contractor.contract_date
            initial['note'] = contractor.note
            initial['cell_phone'] = contact.cell_phone
            initial['home_phone'] = contact.home_phone
            initial['other_phone'] = contact.other_phone
            initial['email'] = contact.email
            initial['id_zipcode'] = address.id_zipcode
            initial['id_address1'] = address.id_address1
            initial['id_address2'] = address.id_address2
            initial['id_address3'] = address.id_address3
            initial['dm_zipcode'] = address.dm_zipcode
            initial['dm_address1'] = address.dm_address1
            initial['dm_address2'] = address.dm_address2
            initial['dm_address3'] = address.dm_address3
        return self.form_class(initial=initial)

    def get_context_data(self, **kwargs):
        context = super(ContractRegisterView, self).get_context_data(**kwargs)
        cont_id = self.request.GET.get('cont_id')
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['order_groups'] = OrderGroup.objects.filter(project=self.get_project())
        context['types'] = UnitType.objects.filter(project=self.get_project())
        contract_units = ContractUnit.objects.filter(project=self.get_project(),
                                                     unit_type=self.request.GET.get('type'),
                                                     contract__isnull=True)
        if cont_id:
            contract_units = ContractUnit.objects.filter(Q(pk=self.request.GET.get('contract_unit')) |
                                                         Q(project=self.get_project(),
                                                           unit_type=self.request.GET.get('type'),
                                                           contract__isnull=True))
        context['contract_units'] = contract_units if cont_id else contract_units[:10]
        context['unit_numbers'] = UnitNumber.objects.filter(project=self.get_project(),
                                                            unit_type=self.request.GET.get('type'),
                                                            contract_unit__isnull=True)
        if self.request.GET.get('unit_number'):
            context['unit_numbers'] = UnitNumber.objects.filter(Q(pk=self.request.GET.get('unit_number')) |
                                                                Q(project=self.get_project(),
                                                                  unit_type=self.request.GET.get('type'),
                                                                  contract_unit__isnull=True))
        context['project_bank_accounts'] = ProjectBankAccount.objects.filter(project=self.get_project())
        pay_code = '4' if cont_id else '2'
        context['installment_orders'] = InstallmentPaymentOrder.objects.filter(project=self.get_project(),
                                                                               pay_code__lte=pay_code)
        context['formset'] = self.PaymentInlineFormSet(queryset=ProjectCashBook.objects.none(),
                                                       form_kwargs={'project': self.get_project()})
        if cont_id:
            contract = context['contract'] = Contract.objects.get(pk=cont_id)
            contractor = context['contractor'] = contract.contractor
            context['task'] = contractor.status if contractor.status >= '3' else '3'
            context['formset'] = self.PaymentInlineFormSet(instance=contract,
                                                           queryset=ProjectCashBook.objects.filter(contract=contract,
                                                                                                   installment_order__pay_sort='1').order_by('deal_date'),
                                                           form_kwargs={'project': self.get_project()})
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        cont_id = self.request.GET.get('cont_id')

        if form.is_valid():

            with transaction.atomic():  # 트랜잭션

                # 1. 계약정보 테이블 입력
                if not cont_id:
                    contract = Contract(project=Project.objects.get(pk=self.request.POST.get('project')),
                                        order_group=OrderGroup.objects.get(pk=self.request.POST.get('order_group')),
                                        serial_number=f"{ContractUnit.objects.get(pk=self.request.POST.get('contract_unit')).unit_code}-{self.request.POST.get('order_group')}",
                                        register=self.request.user)
                else:
                    contract = Contract.objects.get(pk=cont_id)
                    contract.order_group = OrderGroup.objects.get(pk=self.request.POST.get('order_group'))
                    contract.serial_number = f"{ContractUnit.objects.get(pk=self.request.POST.get('contract_unit')).unit_code}-{self.request.POST.get('order_group')}"
                    contract.register = self.request.user
                contract.save()

                # 2. 계약 유닛 연결
                if not cont_id:
                    contractunit = ContractUnit.objects.get(pk=self.request.POST.get('contract_unit'))
                    contractunit.contract = contract
                    contractunit.save()
                else:
                    # 1) 종전 동호수 연결 해제
                    try:
                        pastUN = contract.contractunit.unitnumber
                        pastUN.contract_unit = None  # 종전 계약의 동호수 삭제
                        pastUN.save()
                    except ObjectDoesNotExist:
                        pass

                    # 3. 계약 유닛 연결
                    pastCU = contract.contractunit
                    pastCU.contract = None  # 종전 계약의 계약유닛 삭제
                    pastCU.save()
                    contractunit = ContractUnit.objects.get(pk=self.request.POST.get('contract_unit'))
                    contractunit.contract = contract
                    contractunit.save()

                # 3. 동호수 연결
                if self.request.POST.get('unit_number'):
                    unit_number = UnitNumber.objects.get(pk=self.request.POST.get('unit_number'))
                    unit_number.contract_unit = contractunit
                    unit_number.save()

                # 4. 계약자 정보 테이블 입력
                if not cont_id:
                    contractor = Contractor(contract=Contract.objects.last(),
                                            name=form.cleaned_data.get('name'),
                                            birth_date=form.cleaned_data.get('birth_date'),
                                            gender=form.cleaned_data.get('gender'),
                                            is_registed=form.cleaned_data.get('is_registed'),
                                            status=self.request.POST.get('task'),
                                            reservation_date=form.cleaned_data.get('reservation_date'),
                                            contract_date=form.cleaned_data.get('contract_date'),
                                            note=form.cleaned_data.get('note'),
                                            register=self.request.user)
                else:
                    contractor = Contractor.objects.get(contract=contract)
                    contractor.name = form.cleaned_data.get('name')
                    contractor.birth_date = form.cleaned_data.get('birth_date')
                    contractor.gender = form.cleaned_data.get('gender')
                    contractor.is_registed = form.cleaned_data.get('is_registed')
                    contractor.status = form.cleaned_data.get('task')
                    contractor.reservation_date = form.cleaned_data.get('reservation_date')
                    contractor.contract_date = form.cleaned_data.get('contract_date')
                    contractor.note = form.cleaned_data.get('note')
                    contractor.register = self.request.user
                contractor.save()

                # 5. 계약자 주소 테이블 입력
                if not cont_id:
                    contractorAddress = ContractorAddress(contractor=contractor,
                                                          id_zipcode=form.cleaned_data.get('id_zipcode'),
                                                          id_address1=form.cleaned_data.get('id_address1'),
                                                          id_address2=form.cleaned_data.get('id_address2'),
                                                          id_address3=form.cleaned_data.get('id_address3'),
                                                          dm_zipcode=form.cleaned_data.get('dm_zipcode'),
                                                          dm_address1=form.cleaned_data.get('dm_address1'),
                                                          dm_address2=form.cleaned_data.get('dm_address2'),
                                                          dm_address3=form.cleaned_data.get('dm_address3'),
                                                          register=self.request.user)
                else:
                    contractorAddress = ContractorAddress.objects.get(contractor=contractor)
                    contractorAddress.id_zipcode = form.cleaned_data.get('id_zipcode')
                    contractorAddress.id_address1 = form.cleaned_data.get('id_address1')
                    contractorAddress.id_address2 = form.cleaned_data.get('id_address2')
                    contractorAddress.id_address3 = form.cleaned_data.get('id_address3')
                    contractorAddress.dm_zipcode = form.cleaned_data.get('dm_zipcode')
                    contractorAddress.dm_address1 = form.cleaned_data.get('dm_address1')
                    contractorAddress.dm_address2 = form.cleaned_data.get('dm_address2')
                    contractorAddress.dm_address3 = form.cleaned_data.get('dm_address3')
                    contractorAddress.register = self.request.user
                contractorAddress.save()

                # 6. 계약자 연락처 테이블 입력
                if not cont_id:
                    contractorContact = ContractorContact(contractor=contractor,
                                                          cell_phone=form.cleaned_data.get('cell_phone'),
                                                          home_phone=form.cleaned_data.get('home_phone'),
                                                          other_phone=form.cleaned_data.get('other_phone'),
                                                          email=form.cleaned_data.get('email'),
                                                          register=self.request.user)
                else:
                    contractorContact = ContractorContact.objects.get(contractor=contractor)
                    contractorContact.cell_phone = form.cleaned_data.get('cell_phone')
                    contractorContact.home_phone = form.cleaned_data.get('home_phone')
                    contractorContact.other_phone = form.cleaned_data.get('other_phone')
                    contractorContact.email = form.cleaned_data.get('email')
                    contractorContact.register = self.request.user
                contractorContact.save()

                # 7. 계약금 -- 수납 정보 테이블 입력 -- PaymentInlineFormSet 처리
                if not cont_id:
                    formset = self.PaymentInlineFormSet(self.request.POST,
                                                        form_kwargs={'project': self.request.POST.get('project')})
                else:
                    formset = self.PaymentInlineFormSet(self.request.POST,
                                                        form_kwargs={'project': self.request.POST.get('project')},
                                                        instance=contract)

                if formset.is_valid():
                    cont_note = form.cleaned_data.get('note')
                    for form in formset:
                        pCashbook = form.save(commit=False)
                        pCashbook.project = Project.objects.get(pk=self.request.POST.get('project'))
                        pCashbook.is_contract_payment = True
                        pCashbook.cash_category1 = 1
                        sort = int(contract.order_group.sort)
                        pCashbook.project_account_d1 = ProjectAccountD1.objects.get(pk=sort)
                        pCashbook.project_account_d2 = ProjectAccountD2.objects.get(pk=sort)
                        if not cont_id:
                            pCashbook.contract = contract
                        pCashbook.note = cont_note
                        pCashbook.recoder = self.request.user
                        pCashbook.save()

                return redirect(self.get_back_url())
        else:
            return render(request, 'rebs_contract/contract_form.html', {'formset': formset})


class ContractorUpdate(LoginRequiredMixin, FormView):
    pass


class ContractorTrans(LoginRequiredMixin, FormView):

    model = Contractor

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_context_data(self, **kwargs):
        context = super(ContractorTrans, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        return context


class ContractorReleaseRegister(LoginRequiredMixin, ListView, FormView):

    model = ContractorRelease
    form_class = ContractorReleaseForm
    paginate_by = 10
    template_name = 'rebs_contract/release_form.html'

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_form(self, form_class=None):
        initial = {
            'project': self.get_project(),
            'contractor': self.request.GET.get('contractor'),
            'status': self.request.GET.get('task'),
            'register': self.request.user
        }
        release_id = self.request.GET.get('release_id')
        if release_id:
            release = ContractorRelease.objects.get(pk=release_id)
            initial['refund_amount'] = release.refund_amount
            initial['refund_account_bank'] = release.refund_account_bank
            initial['refund_account_number'] = release.refund_account_number
            initial['refund_account_depositor'] = release.refund_account_depositor
            initial['request_date'] = release.request_date
            initial['completion_date'] = release.completion_date
        return self.form_class(initial=initial)

    def get_context_data(self, **kwargs):
        context = super(ContractorReleaseRegister, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['contractors'] = Contractor.objects.filter(contract__project=self.get_project(), status='2')
        if self.request.GET.get('contractor'):
            context['contractors'] = Contractor.objects.filter(pk=self.request.GET.get('contractor'))
            context['contractor'] = Contractor.objects.get(pk=self.request.GET.get('contractor'))
            context['contract'] = context['contractor'].contract
        context['total_release'] = self.model.objects.filter(project=self.get_project()).count()
        return context

    def get_queryset(self):
        release = self.model.objects.filter(project=self.get_project()).order_by('-id')
        return release

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.GET.get('release_id'):
            release = ContractorRelease.objects.get(pk=request.GET.get('release_id'))
            form = self.form_class(request.POST, instance=release)

        if form.is_valid():
            with transaction.atomic():  # 트랜잭션

                if request.GET.get('task') == '4':

                    # 1. 계약자 정보 현재 상태 변경
                    contractor = Contractor.objects.get(pk=request.POST.get('contractor'))
                    contractor.is_registed = False
                    contractor.status = str(int(contractor.status) + 2)
                    contractor.register = request.user
                    contractor.save()
                    # 2. 계약 상태 변경
                    contract = Contract.objects.get(pk=contractor.contract.id)
                    contract.serial_number = str(contract.serial_number) + '-terminated-' + str(form.cleaned_data.get('completion_date'))
                    contract.activation = False
                    contract.save()
                    # 3. 계약유닛 연결 해제
                    contractunit = ContractUnit.objects.get(contract__contractor=contractor)
                    contractunit.contract = None
                    contractunit.save()
                    # 4. 해당 납부분담금 환불처리
                    projectCash = ProjectCashBook.objects.filter(cash_category1='1', contract=contractor.contract)
                    for pc in projectCash:
                        refund_d2 = pc.project_account_d1.id + 61
                        pc.project_account_d2 = ProjectAccountD2.objects.get(pk=refund_d2)
                        pc.is_refund_closing = contractor
                        msg = str(form.cleaned_data.get('completion_date')) + ' 환불건'
                        append_note = ', ' + msg if pc.note else msg
                        pc.note = pc.note + append_note
                        pc.save()

                # 4. 계약 해지 정보 테이블 입력
                form.save()

                return redirect(reverse_lazy('rebs:contract:release') + '?project=' + str(self.get_project().id))
        else:
            return render(request, 'rebs_contract/release_form.html', {'form': form})


class BuildDashboard(LoginRequiredMixin, TemplateView):

    template_name = 'rebs_contract/dashboard.html'

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_context_data(self, **kwargs):
        context = super(BuildDashboard, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['types'] = UnitType.objects.filter(project=self.get_project())
        context['max_floor'] = UnitNumber.objects.aggregate(Max('floor_no'))
        floor_no__max = context['max_floor']['floor_no__max'] if context['max_floor']['floor_no__max'] else 1
        context['max_floor_range'] = range(1, floor_no__max + 1)
        context['unit_numbers'] = UnitNumber.objects.filter(project=self.get_project())
        context['is_hold'] = UnitNumber.objects.filter(project=self.get_project(), is_hold=True)
        context['is_apply'] = Contractor.objects.filter(contract__project=self.get_project(), status='1')
        context['is_contract'] = Contractor.objects.filter(contract__project=self.get_project(), status='2')
        context['dong_list'] = []
        context['line'] = []
        context['units'] = []

        dong_list = UnitNumber.objects.order_by().values('bldg_no').distinct()

        for dong in dong_list:
            context['dong_list'].append(dong['bldg_no'])
            lines = UnitNumber.objects.order_by('-bldg_line').values('bldg_line').filter(
                bldg_no__contains=dong['bldg_no']).distinct()
            ln = []
            for line in lines:
                ln.append(line['bldg_line'])
            context['line'].append(ln)
            context['units'].append(
                UnitNumber.objects.filter(bldg_no__contains=dong['bldg_no']).order_by('-floor_no', 'bldg_line'))

        context['line'] = list(reversed(context['line']))
        context['units'] = list(reversed(context['units']))
        return context
