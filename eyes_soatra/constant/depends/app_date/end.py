#!python3
depends = [
    '受付終了日',
    '申請終了日',
    '応募締切',
    '提出期限'
    
    # gets
    "受付終了",
    "提出期日",
    "申請期限",
    "申込期限",
    "申請期日"
]

if __name__ == '__main__':
    length = len(depends[0])
    
    for each in depends:
        if length > len(each):
            length = len(each)
    
    print(length)