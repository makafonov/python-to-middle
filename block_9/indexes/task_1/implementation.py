from django.db.models import (
    Func,
    QuerySet,
    Value, Q,
)

from block_9.indexes.task_1.models import (
    Employee,
)


def filter_by_fio(fio) -> QuerySet:
    """Возвращает сотрудников, отфильтрованных по ФИО."""
    employees = Employee.objects.annotate(
        fio=Func(
            Value(' '),
            'fname',
            'iname',
            'oname',
            function='concat_ws',
        ),
    )

    _fio = fio.split()
    if len(_fio) == 3:
        fname, iname, oname = _fio
        qs_filter = Q(fname=fname, iname=iname, oname=oname)
    else:
        qs_filter = Q(fio=fio)

    return employees.filter(qs_filter)


def filter_works_by_period(begin, end) -> QuerySet:
    """Возвращает сотрудников, работавших в заданном периоде хотя бы один день."""
    return Employee.objects.filter(begin__lte=end, end__gte=begin)


def filter_by_country(country) -> QuerySet:
    """Возвращает сотрудников, отфильтрованных по стране."""
    return Employee.objects.filter(country=country)


def filter_by_word_in_additional_info(word) -> QuerySet:
    """Возвращает сотрудников, отфильтрованных по слову в дополнительной информации."""
    return Employee.objects.filter(additional_info__icontains=word)
