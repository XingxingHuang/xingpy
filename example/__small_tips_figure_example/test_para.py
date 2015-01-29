import pdb
#  globle: used for test globle
#  testa   : used for test the param in main
#  testb   : used for test the param in
#
globle = 'globle'
print globle


def run(a):
    print globle

    print 'in progra a: ',a
    a = 'changed in program'
    print 'change a to: ',a
    b ='changeinrun'
    
    
if __name__ == '__main__':
    print globle


    a = 'inmain'
    b = 'testb'
    
    print 'out program  a: ',a
    run(a)
    print 'the end  a,b: ',a,b   
    pdb.set_trace() 