# 电子词典
# 功能说明：
# １　用户可以登录和注册
#     登录凭借用户名密码即可
#     注册要求用户必须填写用户名和密码其他内容自定
#     用户名要求不能够重复
#
# ２　用户数据要求使用数据库长期保存
#     数据报自定
#
# ３　能够满足多个用户同时登陆操作的需求
#
# ４　功能分为客户端和服务端，客户端主要发起请求，服务
#     端处理请求，用户启动客户端即进入一级界面
#         登陆　　注册　 退出
#
# ５　用户登录后即进入二级界面
#     　　查单词　查看历史记录　退出
#
#     查单词：输入单词，显示单词意思，可以循环查询．
#         输入##表示退出查词
#         每行一个单词
#         单词和解释之间一定有空格，后面的单词一定比前面的大
#     查看历史记录：　查看当前用户的历史查词记录
#         name word time
#     退出：退出到一级界面，相当于注销

#'\b.*?\n' 匹配单行
#'\b(\w+)\s+(.*[^ ]*)'　匹配单行内容

import pymysql,re,asyncio,time,pickle
class my_sql(object):
    def __init__(self):
        self.host = '176.216.1.254'
        self.db = pymysql.connect(host =self.host,user = 'root',password ='liu',
                                  port=3306,database='text', charset='utf8')
        self.cur = self.db.cursor()
        self.table_user = 'userpsd'
        self.table_dict = 'dict'
        self.table_record= 'record'
        self.db.commit()

    def sql_exists(self):#判断表是否存在，不存在自动创建
        tablename_list = [self.table_user,self.table_dict,self.table_record]
        for i in tablename_list:
            sql = "SELECT table_name FROM information_schema.TABLES WHERE table_name = '%s';"%i
            self.cur.execute(sql)
            _ =self.cur.fetchone()
            if _:
                print(i,'存在',_)
            else:
                print(i,'不存在，正在插入')
                if i == self.table_user:
                    self.create_table_user()
                elif i ==self.table_dict:
                    self.create_table_dict()
                elif i == self.table_record:
                    self.create_table_record()
            self.db.commit()

    def create_table_user(self):#创建user表
        sql ='''CREATE TABLE `%s` (
                `username`  varchar(20) NOT NULL ,
                `password`  varchar(16) NULL ,
                PRIMARY KEY (`username`),
                INDEX `username` (`username`) 
                )
                ENGINE=InnoDB
                DEFAULT CHARACTER SET=utf8
                ROW_FORMAT=DYNAMIC
                ; '''%self.table_user
        self.cur.execute(sql)

    def create_table_dict(self):#创建字典表
        sql ='''CREATE TABLE `%s` (
                `key_`  varchar(50) NULL ,
                `values_`  text NULL)
                ENGINE=InnoDB
                DEFAULT CHARACTER SET=utf8;'''%self.table_dict
        self.cur.execute(sql)

    def create_table_record(self):#创建纪录表
        sql = '''CREATE TABLE `%s` (
                `username`  varchar(20) NULL ,
                `word`  varchar(50) NULL ,
                `time`  timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
                )
                ENGINE=InnoDB
                DEFAULT CHARACTER SET=utf8
                ;'''%self.table_record
        self.cur.execute(sql)

    def login_(self,user,psd):
        sql = "SELECT username,password from %s where username='%s' and password='%s'"%(self.table_user,user,psd)
        a = self.sql_sql(sql)
        if a:
            print('登陆成功',a)
            login_su = '登陆成功suc,user=%s,psd=%s'%(user,psd)
            return login_su
        else:
            print('登陆失败，用户名或密码不存在')
            login_bad = '登陆失败bad,user=%s,psd=%s' % (user, psd)
            return login_bad

    def regit_(self,user,psd):
        message_ = self.login_(user,psd)
        print(message_)
        suc_ = message_.find('suc')
        bad_ =message_.find('bad')
        if suc_ > 0:
            return '用户已存在'
        elif bad_ > 0:
            if user and psd:
                print('正在创建用户')
                sql = "insert into %s VALUES('%s','%s')"%(self.table_user,user,psd)
                a = self.sql_sql(sql)
                self.db.commit()
                return '用户创建成功'

    def sql_sql(self,sql,one =True):#提交SQL语句，FASLE时，返回查询结果多条
        try:
            self.cur.execute(sql)
            if one:
                return self.cur.fetchone()
            else:
                return self.cur.fetchall()
        except:self.db.rollback()


class dict_re(my_sql):#dict单词部分的解释并插入表纪录
    def __init__(self):
        super().__init__()
    def insert_d(self):
        _ = 0
        pattern = r'\b(\w+)\s+(.*[^ ]*)'
        with open('dict.txt','r') as f:
            while True:
                text_ = f.readline()
                if not text_:
                    break

                try:
                    a = re.search(pattern,text_)
                    sql = 'insert into %s VALUES("%s","%s")'%(self.table_dict,a.group(1),a.group(2))
                    self.sql_sql(sql)
                    _ +=1
                    if _ > 20:
                        self.db.commit()
                        print('提交成功%s'%_)
                        _ = 0
                except:
                    print('出错')

import selectors,socket
class sock_(my_sql):
    def __init__(self):
        super().__init__()
        self.s = socket.socket()
        #self.s.setblocking(False)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.epoll = selectors.DefaultSelector()
        self.s.bind(('127.0.0.1',8080))
        self.s.listen()
        self.epoll.register(self.s,selectors.EVENT_READ,self.accept_)
        self.info = ['登录','注册','查词']

    def accept_(self,s):
        conn,addr = s.accept()
        print('正在注册')
        self.epoll.register(conn,selectors.EVENT_READ,self.recv_)

    def recv_(self,conn):#注册recv来进行消息的判断执行函数
        try:
            date = conn.recv(1024).decode()
            print(date)
            if not date:
                conn.close()
                self.epoll.unregister(conn)
                print('已结束')

            if date == '注册':
                self.u_(conn)

            elif date == '登录':
                self.u_(conn,True)

            elif date == '查词':
                self.select_dic(conn)

            elif date == '查纪录':
                print('查纪录进来')
                self.select_history(conn)

        except:
            conn.close()
            self.epoll.unregister(conn)

    def select_history(self,conn):#发送历史纪录
        data = conn.recv(1024).decode()
        sql = "select word from %s where username='%s'"%(self.table_record,data)
        c= self.sql_sql(sql,False)
        conn.send(pickle.dumps(c))

    def select_dic(self,conn):#获取单词的解释发送并存储到历史纪录表
        data = conn.recv(1024).decode().split('|||')#获取的是单词
        print(data)
        sql = "select values_ from %s where key_='%s'"%(self.table_dict,data[0])
        a= self.sql_sql(sql)[0]
        conn.send(a.encode())
        sql = "insert into %s(username,word) VALUES('%s','%s')"%(self.table_record,data[1],data[0])
        suc = self.sql_sql(sql)
        self.db.commit()
        print('纪录插入成功')

    def u_(self,conn,login = False):#用户的登录和注册前
        data = conn.recv(1024).decode()
        suc = self.u_p_tq(data)
        if login:
            print(suc)
            suc =self.login_(suc[0],suc[1])
        else:

            suc = self.regit_(suc[0], suc[1])
        conn.send(suc.encode())

    def u_p_tq(self,data):#提取账号，密码返回
        print(data)
        us_ = data.find(':#')
        ue_ = data.find('###')
        ps_ = data.find('|')
        pe_ = data.find('||')
        u = data[us_ + len(':#'):ue_]
        p = data[ps_ + 1:pe_]
        return [u,p]

    def monit_(self):
        while True:
            event = self.epoll.select()
            for fo,ev in event:
                callback = fo.data
                callback(fo.fileobj)
if __name__ == '__main__':
    s = sock_()
    s.monit_()


