import time
from datetime import datetime
def get_access():
	dt = datetime.fromtimestamp(int(time.time()))
	today = str(dt.year)+'.'+str(dt.month)+'.'+str(dt.day)
	with open('../log.log','r+') as log:
		string=log.readline()
		while string:
			if string[0]=='I':
				if string[5]=='a':
					with open('../access/'+today+'_access.log','a+') as acc:
						acc.write(string)
			string = log.readline()
		log.truncate(0)
if __name__ == '__main__':
	get_access()
