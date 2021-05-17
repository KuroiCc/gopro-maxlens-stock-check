import smtplib
from email.mime.text import MIMEText
import time
import requests
from bs4 import BeautifulSoup


class Pygmail():
    def __init__(self, address, password):
        self.address = address
        self.password = password

        self.HOST = 'smtp.gmail.com'
        self.PORT = 587

        self.smtp = smtplib.SMTP(self.HOST, self.PORT)
        # self.smtp.set_debugle vel(1)

    def connet(self):
        try:
            print('connect %s:%s ... ' % (self.HOST, self.PORT), end='')
            self.smtp.connect(self.HOST, self.PORT)
            print('Successed')
        except:
            print('connect failed')

    def login(self):
        try:
            self.smtp.starttls()
            print('loginning ... ', end='')
            self.smtp.login(self.address, self.password)
            print('Successed.')
        except:
            print('login faild.')

    def send_mail(self, to_address, subject, bodytext):
        try:
            msg = MIMEText(bodytext, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = self.address
            msg['To'] = to_address
            self.connet()
            self.login()
            self.smtp.send_message(msg)
            print('Mail sent to (%s) successfully' % to_address)
        except:
            print('send mail faild ...')

        self.quit()

    def quit(self):
        self.smtp.quit()
        print('mail quit.')

    def close(self):
        self.smtp.close()
        print('disconnected mail server.')


class stock_check():
    def __init__(self, target_url):
        self.target_url = target_url
        self.WAIT_INTERVAL = 180
        self.now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # write log
    def log(self, out_file, content):
        self.now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        with open(out_file, 'a', encoding='utf-8') as add:
            add.write(self.now + ' ' + content + '\n')

    # connect URL get whole HTML
    def crawl(self):
        self.response = requests.get(self.target_url, timeout=10)
        self.response.encoding = self.response.apparent_encoding
        self.bs = BeautifulSoup(self.response.text, 'html.parser')


if __name__ == '__main__':
    your_email = "your email"
    your_password = "your password"
    to_email = "to email"

    out_file2 = 'Gopro Max Lens stock check_log.txt'
    target_url = 'https://gopro.com/ja/jp/shop/mounts-accessories/hero9-black-max-%E3%83%AC%E3%83%B3%E3%82%BA%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%A9%E3%83%BC/ADWAL-001.html'
    target_url2 = 'https://gopro.com/ja/jp/shop/mounts-accessories/%E3%83%87%E3%82%A3%E3%82%B9%E3%83%97%E3%83%AC%E3%82%A4%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%A9%E3%83%BC/AJLCD-001-EU.html'
    target_url3 = '192.168.0.0'
    target_tag = '#add-to-cart'

    max_lens = stock_check(target_url)
    pygmail = Pygmail(your_email, your_password)
    day = time.time()
    times = 1

    msg = 'stock checker start.....'
    max_lens.log(out_file2, msg)
    print(max_lens.now, msg)

    while True:
        print('day:%d, %d times checking stock.....' %
              ((time.time() - day) // 86400 + 1, times),
              end='')
        try:
            max_lens.crawl()
            status = max_lens.bs.select(target_tag)[0].text
        except:
            error_mes = 'get stock status faild'
            print(error_mes + '##########')
            max_lens.log(out_file2, error_mes)
            pygmail.send_mail(to_email, 'stock_check error',
                              error_mes)
            break

        if status.find('在庫なし') != -1:
            times += 1
            max_lens.log(out_file2, 'status: %s.' % status[:4])
            print('%s. next check after %ds' %
                  (status[:4], max_lens.WAIT_INTERVAL))
            time.sleep(max_lens.WAIT_INTERVAL)
        else:
            max_lens.log(out_file2, 'status: %s.' % status)
            print('%s. ???There is something. Sand Mail' % status)
            mainbody = 'Gopro status: %s.\n\nThere is something.\nGO  GO  GO  GO  GO  GO  GO!!!!\n\nlink:\n%s' % (
                status, max_lens.target_url)
            pygmail.send_mail(to_email,
                              'Gopro status: %s.' % status, mainbody)
            break

    print('done!')
