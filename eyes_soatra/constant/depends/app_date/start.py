#!python3
depends = [
    '受付開始日',
    '申請開始日',
    '提出開始',
    
    # get
    "申込開始日",
    "申請の受付開始日",
    "申請受付開始日"
]

if __name__ == '__main__':
    length = len(depends[0])
    
    for each in depends:
        if length > len(each):
            length = len(each)
    
    print(length)