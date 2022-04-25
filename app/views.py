import pymysql
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect, HttpResponse

from app.models import Classes, Students, Teachers, TeacherToClass
from utils import sqlhelper
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required


# Create your views here.
def login(request):
    '''
    用户登录
    :param request:
    :return:
    '''
    username = request.POST.get('username')
    pwd = request.POST.get('pwd')
    if request.method == 'POST':
        user = authenticate(username=username, password=pwd)
        if user is not None:
            auth_login(request, user)
            obj = redirect('/user/classes/')
            return obj
    else:
        return render(request, 'login.html')


def logout(request):
    auth_logout(request)  # 会清除 cookie,seesion
    obj = redirect('/user/login/')
    return obj


@login_required
def classes(request):
    """
    查询班级信息
    :param request:
    :return:
    """
    class_list = Classes.objects.all()
    # [{'id': 1, 'title': '软件工程'}, {'id': 3, 'title': '网络工程'}, {'id': 4, 'title': '计算机科学与技术'}]

    return render(request, 'class.html', {'class_list': class_list})


@login_required
def add_class(request):
    """
    添加班级信息
    :param request:
    :return:
    """
    # 如果是get请求就返回add_class.html模板就可以
    if request.method == 'GET':
        return render(request, 'add_class.html')
    # 如果是post请求则执行下面的代码
    else:
        # 获取班级的标题
        class_title = request.POST.get('class_title')
        print(class_title)
        c = Classes(title=class_title)
        c.save()
        return redirect('/user/classes/')


@login_required
def edit_class(request):
    """
    编辑班级信息
    :param request:
    :return:
    """
    # 如果是get请求，这里额外也需要查询下数据库，把原来的信息也展示出来
    if request.method == 'GET':
        # 获取客户端传过来的班级id
        nid = request.GET.get('nid')
        # 创建数据库连接
        result = Classes.objects.get(id=nid)
        # print(result)
        # {'id': 1, 'title': '软件工程'}

        return render(request, 'edit_class.html', {'result': result})
    # post请求用来修改班级信息
    else:
        # nid = request.POST.get('nid')  # 放到请求体
        nid = request.GET.get('nid')  # 放到请求头
        title = request.POST.get('title')
        # 创建数据库连接
        Classes.objects.filter(id=nid).update(title=title)
        return redirect('/user/classes/')


@login_required
def del_class(request):
    # 获取客户端传过来的nid，我们要个根据nid来删除数据
    nid = request.GET.get('nid')
    # 创建连接对象
    Classes.objects.filter(id=nid).delete()

    return redirect('/user/classes/')


@login_required
def student(request):
    '''
    学生信息列表
    :param request:封装了请求相关的所有信息
    :return:返回模板和数据
    '''
    # 创建连接对象
    student_list = Students.objects.all()

    paginator = Paginator(student_list, 10)
    current_page = request.GET.get('page')
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger as e:
        posts = paginator.page(1)
    except EmptyPage as e:
        posts = paginator.page(1)
    # 查询班级信息
    class_list = list(Classes.objects.all().values())
    return render(request, 'student.html', {'student_list': student_list, 'class_list': class_list, 'posts': posts})


@login_required
def add_student(request):
    """
    添加学生信息
    :param request:
    :return:
    """
    # 如果是get请求
    if request.method == 'GET':
        classe_list = Classes.objects.all()
        return render(request, 'add_student.html', {'class_list': classe_list})
    # 如果是post请求
    else:
        # 获取学生的名字
        name = request.POST.get('name')
        # 获取学生的班级id
        class_id = request.POST.get('class_id')
        c1 = Classes.objects.filter(id=class_id).get()
        s = Students(name=name, classes=c1)
        s.save()
        return redirect('/user/student/')


@login_required
def edit_student(request):
    """
    编辑学生信息
    :param request:
    :return:
    """
    # get请求时
    if request.method == 'GET':
        # 获取传过来的学生id
        nid = request.GET.get('nid')
        # 创建连接对象
        class_list = Classes.objects.all()
        current_student_info = Students.objects.filter(id=nid).get()
        return render(request, 'edit_student.html',
                      {'class_list': class_list, 'current_student_info': current_student_info})
        # post请求时
    else:
        # 从url中获取学生的id
        nid = request.GET.get('nid')
        # 从请求体(form表单)中获取当前学生的姓名
        name = request.POST.get('name')
        # 从请求体中获取当前学生的班级id
        class_id = request.POST.get('class_id')
        # 创建练级
        c1 = Classes.objects.filter(id=class_id).get()
        Students.objects.filter(id=nid).update(name=name, classes=c1)

        return redirect('/user/student/')


@login_required
def del_student(request):
    """
    删除学生信息
    :param request:
    :return:
    """
    # 获取学生编号
    nid = request.GET.get('nid')
    Students.objects.filter(id=nid).delete()
    return redirect('/user/student/')


@login_required
def add_class_modal(request):
    """
    模态对话框的方式添加班级信息
    :param request:
    :return:
    """
    # 从前台ajax提交的json字符串中{'title': $('#title').val()}获取班级名称
    title = request.POST.get('title')
    # 输入的班级名称的长度需要大于0
    # print(title)
    if len(title) > 0:
        # 创建连接
        c = Classes(title=title)
        c.save()
        # 向前台返回ok
        return HttpResponse('ok')
    else:
        # 如果提交过来的班级名称长度是小于0的,向前台返回不能为空，给前台提示信息
        return HttpResponse('班级不能为空！')


@login_required
def edit_class_modal(request):
    '''
    模态对话框编辑班级信息
    '''
    # 获取班级编号
    class_id = request.GET.get('class_id')
    # 获取班级名称
    class_title = request.GET.get('class_title')
    # 获取的名称长度要大于0
    if len(class_title) > 0:
        # 创建连接
        Classes.objects.filter(id=class_id).update(title=class_title)

        return HttpResponse('ok')
    else:
        # 返回错误提示信息
        return HttpResponse('班级不能为空！')


@login_required
def del_class_modal(request):
    """
    模态对话框删除班级信息
    :param request:
    :return:
    """
    # 获取班级编号，需要通过编号删除班级信息
    class_id = request.GET.get('class_id')
    # 创建连接
    Classes.objects.filter(id=class_id).delete()

    return HttpResponse('ok')


@login_required
def add_student_modal(request):
    """
    模态对话框的方式添加班级信息
    :param request:
    :return:
    """
    ret = {'status': True, 'msg': None}
    try:
        name = request.POST.get('name')
        class_id = request.POST.get('class_id')
        if len(name) <= 0 or len(class_id) <= 0:
            ret['status'] = False
            ret['msg'] = '学生姓名或班级不能为空'
            return HttpResponse(json.dumps(ret))
        c1 = Classes.objects.filter(id=class_id).get()
        s = Students(name=name, classes=c1)
        s.save()
    except Exception as e:
        ret['status'] = False
        ret['msg'] = str(e)
    return HttpResponse(json.dumps(ret))


@login_required
def edit_student_modal(request):
    """
    模态框编辑学生信息
    :param request:
    :return:
    """
    ret = {'status': True, 'msg': None}
    try:
        student_id = request.POST.get('student_id')
        class_id = request.POST.get('class_id_edit')
        student_name = request.POST.get('student_name')
        c1 = Classes.objects.filter(id=class_id).get()
        Students.objects.filter(id=student_id).update(name=student_name, classes=c1)
    except Exception as e:
        ret['status'] = False
        ret['msg'] = str(e)
    return HttpResponse(json.dumps(ret))


@login_required
def del_student_modal(request):
    """
    模态框删除学生信息
    :param request:
    :return:
    """
    ret = {'status': True, 'msg': None}
    try:
        student_id = request.GET.get('student_id')
        Students.objects.filter(id=student_id).delete()
    except Exception as e:
        ret['status'] = False
        ret['msg'] = str(e)
    return HttpResponse(json.dumps(ret))


@login_required
def add_teacher(request):
    """
    添加教师
    :param request:
    :return:
    """
    if request.method == 'GET':
        class_list = Classes.objects.all()
        return render(request, 'add_teacher.html', {'class_list': class_list})
    else:
        name = request.POST.get('name')
        t = Teachers.objects.create(name=name)
        t.save()
        class_ids = request.POST.getlist('class_ids')  # ['1', '8', '9', '10']
        # 多次连接，多次提交
        t1 = Teachers.objects.filter(id=t.id).get()
        print(type(t))
        print(type(t1))
        data_list = []  # [(9, '8'), (9, '9'), (9, '10')]
        for class_id in class_ids:
            c1 = Classes.objects.filter(id=class_id).get()

            t = TeacherToClass.objects.create(teacher=t1, classes=c1)
            t.save()

        return redirect('/user/teacher/')


@login_required
def teacher(request):
    """
    查询教师和任课班级信息
    :param request:
    :return:
    """
    obj = sqlhelper.SqlHelper()
    teacher_list = obj.get_list(
        'select teacher.id as tid,teacher.name,classes.title from teacher left join teacher2class on teacher.id = teacher2class.teacher_id left join classes on teacher2class.classes_id = classes.id ;',
        [])
    """
    print(teacher_list)
    [
    {'tid': 1, 'name': '李娇', 'title': '网络工程'}, 
    {'tid': 1, 'name': '李娇', 'title': '计算机科学与技术'},
    {'tid': 1, 'name': '李娇', 'title': '软件技术'},
    {'tid': 1, 'name': '李娇', 'title': '软件工程'},
    {'tid': 2, 'name': '李晓', 'title': '网络工程'},
    {'tid': 2, 'name': '李晓', 'title': '软件工程'}
    ]
    """

    result = {}
    for row in teacher_list:
        tid = row['tid']
        if tid in result:
            result[tid]['titles'].append(row['title'])
        else:
            result[tid] = {'tid': row['tid'], 'name': row['name'], 'titles': [row['title'], ]}
    """
    print(ret)
    {
        1: {'tid': 1, 'name': '李娇', 'titles': ['网络工程', '计算机科学与技术', '软件技术', '软件工程']}, 
        2: {'tid': 2, 'name': '李晓', 'titles': ['网络工程', '软件工程']}
    }
    """
    return render(request, 'teacher.html', {'teacher_list': result.values(), })


@login_required
def edit_teacher(request):
    if request.method == 'GET':
        nid = request.GET.get('nid')
        obj = sqlhelper.SqlHelper()
        # 当前教师的信息
        teacher_info = obj.get_one('select id,name from teacher where id = %s', [nid, ])
        # 当前教师的任教班级的id信息
        class_id_list = obj.get_list('select classes_id from teacher2class where teacher_id=%s', [nid, ])
        # 所有的班级信息
        class_list = obj.get_list('select id,title from classes', [])
        """
        print(teacher_list) # {'id': 2, 'name': '李晓'}
        print(class_list) # [{'id': 1, 'title': '软件工程'}, {'id': 8, 'title': '软件技术'}, {'id': 9, 'title': '计算机科学与技术'}, {'id': 10, 'title': '网络工程'}]
        print(class_id_list) # [{'class_id': 1}, {'class_id': 10}]
        """
        obj.close()
        temp = []
        for item in class_id_list:
            temp.append(item['classes_id'])
        """
        print(temp)  # [1, 10]
        """
        return render(request, 'edit_teacher.html',
                      {'class_list': class_list, 'teacher_info': teacher_info, 'class_id_list': temp})
    else:
        # 获取post请求的url上的参数
        nid = request.GET.get('nid')
        print(nid)
        name = request.POST.get('name')
        class_ids = request.POST.getlist('class_ids')  # ['1', '8', '9', '10']
        obj = sqlhelper.SqlHelper()
        obj.modify('update teacher set name = %s where id = %s', [name, nid])
        obj.modify('delete from teacher2class where teacher_id = %s', [nid])
        data_list = []  # [('1', '1'), ('1', '8'), ('1', '9'), ('1', '10')]
        """
        for class_id in class_ids:
            temp = (nid, class_id,)
            data_list.append(temp)
        """
        # 使用lambda表达式
        func = lambda nid, class_id: data_list.append((nid, class_id))
        for class_id in class_ids:
            func(nid, class_id)
        obj.multiple_modify('insert into teacher2class(teacher_id,classes_id) values (%s,%s)', data_list)
        return redirect('/user/teacher/')


@login_required
def add_teacher_modal(request):
    """
    AJAX的方式添加教师信息
    :param request:
    :return:
    """
    if request.method == 'GET':
        class_list = Classes.objects.all()
        return HttpResponse(json.dumps(class_list))
    if request.method == 'POST':
        ret = {'status': True, 'msg': None}
        try:
            name = request.POST.get('name')
            class_ids = request.POST.getlist('class_ids')  # ['1', '8', '9', '10']
            t1 = Teachers.objects.create(name=name)
            t1.save()
            for class_id in class_ids:
                c1 = Classes.objects.filter(id=class_id).get()
                TeacherToClass.objects.create(teacher=t1, classes=c1).save()
        except Exception as e:
            ret['status'] = False
            ret['msg'] = '处理失败!'
        return HttpResponse(json.dumps(ret))


@login_required
def del_teacher_modal(request):
    """
    AJAX的方式删除教师信息
    :param request:
    :return:
    """
    if request.method == 'GET':
        ret = {'status': True, 'msg': None}
        try:
            obj = sqlhelper.SqlHelper()
            tid = request.GET.get('teacher_id')
            obj.modify('delete from teacher where id =%s', [tid])
            obj.modify('delete from teacher2class where teacher_id = %s', [tid])
            obj.close()
        except Exception as e:
            ret['status'] = False
            ret['msg'] = "删除失败！"
        return HttpResponse(json.dumps(ret))
