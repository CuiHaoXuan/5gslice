import random
def cidr():
	cidr_list = [ str(random.randint(0,254))  for i in range(2) ]
	cidr_str ='172.' +  ".".join(cidr_list) + '.0/24'
	print cidr_str

if __name__=='__main__':
	cidr()
