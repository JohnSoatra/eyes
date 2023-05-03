#!python3
import eyes_soatra

result = eyes_soatra.eyes.view_page(
    url = 'http://www.town.shiriuchi.hokkaido.jp/kyoiku/shakai/kominkan/katei/yochien/',
    show_highlight=True
)
print(result)