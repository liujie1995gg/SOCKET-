import socket,time,pickle
class A:
    def __init__(self):
        self.s =socket.socket()
        self.s.connect(('127.0.0.1', 8080))
        self.template_1 = '账号:#{}###密码:|{}||'
        self.funtion = {1:self.login,
                   2:self.regit,
                   3:self.exis_}
        self.direatory={1:'登录',
                   2:'注册',
                   3:'退出'}
        self.funtion2={1:self.select_dic,
                       2:self.select_history,
                       3:self.exis_}
        self.direatory2={1:'查询单词',
                         2:'查询历史记录',
                         3:'退出'}
        self.u = ''

    def start(self):#开始方法
        a = self.dir_()#登录成功后会返回结果
        if a:
            self.dir_2()

    def input_(self):#一级页面input简写
        while True:
            try:
                inp = input('请输入对应编号：')
                inp = int(inp)
                break
            except:
                print('输入有误，请重新输入')
                continue
        return inp

    def dir_(self):#一级页面目录
        while True:
            for i in self.direatory:
                print(i,self.direatory[i])
            inp = self.input_()
            if inp in self.funtion:
                data = self.funtion[inp]()
                if data == '成功':
                    return '成功'
            else:
                print('输入编号有误！')

    def login(self):#一级页面登录
        while True:
            while True:
                try:
                    inp_u = input('请输入注册账号:')
                    inp_p = input('请输入注册密码:')
                    break
                except:
                    print('输入有误：')
                    continue
            bank = self.template_1.format(inp_u,inp_p)
            self.s.send('登录'.encode())
            time.sleep(0.2)
            self.s.send(bank.encode())
            data = self.s.recv(1024).decode()
            print(data)
            if data.find('成功')>0:
                self.u = inp_u
                break
        return '成功'

    def regit(self):#一级页面注册
        while True:
            try:
                inp_u = input('请输入注册账号:').split()
                inp_p = input('请输入注册密码:').split()
            except:
                print('输入有误：')
                continue
            if inp_u and inp_p:
                a = self.template_1.format(inp_u,inp_p)
                self.s.send('注册'.encode())
                time.sleep(0.2)
                self.s.send(a.encode())
                data = self.s.recv(1024).decode()
                print(data)
                if data:
                    break
            else:
                continue

    def dir_2(self):#二级页面目录
        while True:
            for i in self.direatory2:
                print(i,self.direatory2[i])
            inp = self.input_()
            if inp in self.funtion2:
                self.funtion2[inp]()

    def input_2(self,query=False):#二级页面input
        if query:
            inp = '%s'%self.u
        else:
            inp = input('请输入需要查找的单词：')
            inp = ('%s'+'|||'+self.u)%inp
        return inp

    def select_dic(self):#二级页面获取单词信息
        inp = self.input_2()
        self.s.send('查词'.encode())
        time.sleep(0.2)
        self.s.send(inp.encode())
        data = self.s.recv(1024).decode()
        print('查询如下：',data)

    def select_history(self):#二级页面获取历史纪录
        inp = self.input_2(True)
        self.s.send('查纪录'.encode())
        time.sleep(0.2)
        self.s.send(inp.encode())
        _ =b''
        while True:
            data = self.s.recv(1024)
            if len(data) < 1020:
                _ += data
                break
            _ += data
        for i in pickle.loads(_):
            print(i[0])
        print('*'*30)

    def exis_(self):
        exit()
if __name__ == '__main__':
    a = A()
    a.start()
