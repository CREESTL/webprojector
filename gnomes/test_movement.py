from gnomes.Rauds import Scubo


scubo = Scubo()
scubo.move(36, 30)
screen = scubo.get_cur_screen()
x = scubo.x()
y = scubo.y()

print(f'screen is {screen}, x is {x}, y is {y}')
