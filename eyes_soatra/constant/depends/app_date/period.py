#!python3
depends = [
    '受付期間',
    '申請期間',
    '申請受付期間'
    
    # get
    "申出期間",
    "申請の期間",
    "請求期間",
    "貸付期間",
    "応募受付期間",
    "申請時期",
    "貸付の期間",
    "貸与期間",
    "補助申請受付期間",
    "補助受付期間",
]

if __name__ == '__main__':
    length = len(depends[0])
    
    for each in depends:
        if length > len(each):
            length = len(each)
    
    print(length)