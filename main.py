#sprite  #pygame內建精靈，可以用來做很多事情
import pygame
import random
import os
from pygame import transform

from pygame.mixer import Sound, stop

#螢幕、尺寸、更新率
#設定好不會去改的變數，習慣用大寫
WIDTH=500 
HEIGHT=600
FPS=60
#Color
BLACK=(0,0,0)
WHITE=(255,255,255)
GREEN=(0,255,0)
RED=(255,0,0)
YELLOW=(255,255,0)

#遊戲初始化 and 創建視窗
pygame.init()
pygame.mixer.init() #音樂初始化
screen=pygame.display.set_mode((WIDTH,HEIGHT)) #display.set_mode 為pygame內建函式
Game_name = "恩皇出征 ! !"
clock=pygame.time.Clock() #為了解決迴圈速度，管理時間

#載入圖片，需先pygame.init()
#用os載入路徑比較不會出錯，convert把圖片轉換成pygame的格式
#background_img=pygame.image.load("img//background.png").convert()
background_img = pygame.image.load(os.path.join("img","background.png")).convert()
player_img = pygame.image.load(os.path.join("img","player.png")).convert()
player_mini_img = pygame.transform.scale(player_img,(25,19))
player_mini_img.set_colorkey(BLACK)
#小圖示
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img","bullet.png")).convert()
#rock_img = pygame.image.load(os.path.join("img","rock.png")).convert()
rock_imgs = []
for i in range(7):
    #append : 把rock加入列表。
    #字串內加變數 f "{}"
    rock_imgs.append( pygame.image.load(os.path.join("img",f"rock{i}.png")).convert())

#載入一串爆炸圖片，做成動畫
expl_anim = {} #字典存放照片
expl_anim["large"]=[] #一連串照片
expl_anim["small"]=[]
expl_anim["player"]=[]
for i in range(9):
    expl_img =  pygame.image.load(os.path.join("img",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim["large"].append(pygame.transform.scale(expl_img,(75,75)))
    expl_anim["small"].append(pygame.transform.scale(expl_img,(30,30)))
    #player expl
    player_expl_img =  pygame.image.load(os.path.join("img",f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim["player"].append(pygame.transform.scale(expl_img,(100,100)))

power_imgs = {} #寶物字典
power_imgs["shield"] = pygame.image.load(os.path.join("img","shield.png")).convert()
power_imgs["gun"] = pygame.image.load(os.path.join("img","gun.png")).convert()

#載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound","shoot.wav"))
shoot_sound.set_volume(0.5)
player_expl_sound = pygame.mixer.Sound(os.path.join("sound","rumble.ogg"))
expls_sound = [
    pygame.mixer.Sound(os.path.join("sound","expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound","expl1.wav"))
]
gun_sound = pygame.mixer.Sound(os.path.join("sound","pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound","pow0.wav"))
pygame.mixer.music.load(os.path.join("sound","background.ogg"))
pygame.mixer.music.play(-1) #-1代表無限重複撥放
pygame.mixer.music.set_volume(0.3)

#從電腦載入字體
#font_name = pygame.font.match_font("arial") #不支援中文換一個
font_name = os.path.join("font.ttf")
def draw_text(surf,text,size,x,y):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,WHITE) #render渲染, True:使用反鋸齒
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface,text_rect)

def new_rock():
    rock=Rock()
    all_sprites.add(rock)
    rocks.add(rock)

def draw_health(surf,hp,x,y):
    if hp<0:
        hp=0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp /100)*BAR_LENGTH #生命條填滿 %數
    #pygame製作生命條矩形
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT) #填滿外框
    #(surface,color,rect)
    pygame.draw.rect(surf,GREEN,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2) #2 像數    

def draw_lives(surf,lives,img,x,y): 
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 35*i #間隔30像素畫另一個
        img_rect.y = y
        surf.blit(img,img_rect)

def draw_init():
    screen.blit(background_img,(0,0)) 
    draw_text(screen,Game_name,64,WIDTH/2,HEIGHT*0.25)
    draw_text(screen,"← → : 恩皇左欺敵、右欺敵",22,WIDTH/2,HEIGHT*0.5)
    draw_text(screen,"Space : 恩皇請你吃慶記",22,WIDTH/2,HEIGHT*0.55)
    draw_text(screen,"隨便按就開始",18,WIDTH/2,HEIGHT*0.75)
    pygame.display.update()
    watting = True
    while watting:
        clock.tick(FPS)
        #取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP: #按下鬆開才會開始
                watting = False
                return False

class Player(pygame.sprite.Sprite): #以Player繼承內建的Sprite類別
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image=pygame.Surface((50,40)) #一個平面的imag 
        #self.image.fill(player_img)
        self.image = pygame.transform.scale(player_img,(50,38)) #調整圖片大小
        self.image.set_colorkey(BLACK) #把黑色變透明 
        self.rect = self.image.get_rect() #把image用矩形框起來 
        self.radius =20 #碰撞判定，圓形半徑
        #pygame.draw.circle(self.image,RED,self.rect.center,self.radius)#檢查碰撞半徑(畫在這個圖面,顏色,圓心,半徑)
        self.rect.centerx = WIDTH / 2 #rect X位置
        self.rect.bottom = HEIGHT - 10 # bottom 高度放在視窗底部
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

 
    def update(self):
        #設定子彈強化時間
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now
        #hide一段時間後重置飛船位置
        if self.hidden and pygame.time.get_ticks() - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0 :
            self.rect.left = 0  

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet (self.rect.centerx,self.rect.top) #傳入player位置到Bullet
                all_sprites.add(bullet) #把Bullet新增到all_sprites群組
                bullets.add(bullet) #把Bullet新增到sprites群組做碰撞判定
                shoot_sound.play() 
            elif self.gun >=2:
                bullet1 = Bullet (self.rect.left,self.rect.centery) 
                bullet2 = Bullet (self.rect.right,self.rect.centery)
                all_sprites.add(bullet1) 
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2,HEIGHT+500) #把飛船中心移到是窗外
    
    def gunup (self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite): #以Player繼承內建的Sprite類別
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image=pygame.Surface((30,30))  #一個平面的image
        #self.image.fill(RED)
        self.image_ori = random.choice(rock_imgs) #新增一個沒轉動的圖片,讓旋轉每次都從這張圖開始避免疊加旋轉
        self.image_ori.set_colorkey(BLACK)
        self.image  = self.image_ori.copy() #把沒轉動的圖複製過來
        self.rect = self.image.get_rect() #把image用矩形框起來
        self.radius = int(self.rect.width * 0.85 / 2)
        #pygame.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.x = random.randrange(0,WIDTH-self.rect.width) #減去石頭寬度
        self.rect.y = random.randrange(-180,-100) #離視窗頂部0(+0)到視窗以外50(-50)的距離開始掉落
        self.speedy = random.randrange(3,7)
        self.speedx = random.randrange(-2,2) #負的左右都有可能
        self.total_degree = 0
        self.rot_degree = random.randrange(-3,3) #給一個圖片轉動的參數
        
    def rotate(self):
        self.total_degree += self.rot_degree #旋轉每次+3度
        self.total_degree = self.total_degree % 360 #轉動累加到360%重置為0
        self.image = pygame.transform.rotate(self.image_ori , self.total_degree) #每次都丟原始圖片轉動(surface,angle)
        #讓旋轉時也重新定位
        center = self.rect.center #原本的中心點
        self.rect = self.image.get_rect() #轉動後的圖片重新定位
        self.rect.center = center #原本的中心點換成新的中心點

    def update(self):
        self.rotate() #fps 60 一秒轉60次
        self.rect.y += self.speedy #y座標每次加speedy的距離
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0,WIDTH-self.rect.width) #減去石頭寬度
            self.rect.y = random.randrange(-50,0)
            self.speedy = random.randrange(2,6)
            self.speedx = random.randrange(-1,1) #負的左右都有可能

class Bullet(pygame.sprite.Sprite): #以Player繼承內建的Sprite類別
    def __init__(self, x, y): #傳入飛船的x,y資訊
        pygame.sprite.Sprite.__init__(self)
        #self.image=pygame.Surface((10,20)) #一個平面的image
        #self.image.fill(YELLOW)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #把image用矩形框起來
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0: #子彈底部小於0就刪掉
            self.kill() #kill是sprite函數，在所有sprite群組移除

class Explosion(pygame.sprite.Sprite): #以Player繼承內建的Sprite類別
    def __init__(self, center, size): #傳入飛船的x,y資訊
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0] #爆炸的第0張圖片
        self.rect = self.image.get_rect()
        self.rect.center = center
        #因為用FPS更新速度太快，所以做以下處理
        self.frame = 0 #第0張開始更新
        self.last_update = pygame.time.get_ticks() #回傳從初始化到現在的毫秒
        self.frame_rate = 80 #經過幾毫秒更新圖片

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.frame_rate:
            self.last_update = now #把最後更新圖片的時間改成now
            self.frame += 1 #圖片+1
            if self.frame == len(expl_anim[self.size]): #判斷圖片有沒有 = 最後一張
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite): #以Player繼承內建的Sprite類別
    def __init__(self,center): #傳入飛船的x,y資訊
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield","gun"])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #把image用矩形框起來
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT: #子彈底部小於0就刪掉
            self.kill() #kill是sprite函數，在所有sprite群組移除

# #創建all_sprite群組
# all_sprites = pygame.sprite.Group()
# #創建sprite群組，做碰撞判定
# rocks = pygame.sprite.Group()
# bullets = pygame.sprite.Group()
# powers = pygame.sprite.Group()
# player = Player() #綠色為上面的類別class
# all_sprites.add(player) #再all_sprite群組裡面加入player
# for i in range(8): #sprite群組加入rock，用for迴圈生成8個rock
#     new_rock()
#     # rock=Rock()
#     # all_sprites.add(rock) #再all_sprite群組加入rock
#     # rocks.add(rock) #把Rock新增到sprites群組做碰撞判定
# score = 0 

#遊戲迴圈
show_init = True 
running=True
while running:
    #初始畫面
    if show_init:
        #進入init畫面，等到使用者按下任意鍵後跳回
        close = draw_init()
        if close:
            break
        #關閉初始畫面
        show_init = False
        #遊戲重新設定也要重新，所以設置在init階段
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player() #綠色為上面的類別class
        all_sprites.add(player) #再all_sprite群組裡面加入player
        for i in range(8): #sprite群組加入rock，用for迴圈生成8個rock
            new_rock()
        score = 0 


    clock.tick(FPS) #CLOCK.TICK的意思:1秒鐘之內迴圈最多執行次數
    #取得輸入
    for event in pygame.event.get(): #回傳發生的所有事件
        if event.type == pygame.QUIT:
            running=False
        elif event.type == pygame.KEYDOWN: #如果按了按鍵
            if event.key == pygame.K_SPACE:
                player.shoot()

    #更新遊戲
    all_sprites.update() #執行all_sprties群組裡面每一個update函式
    #判斷石頭 子彈相撞
    #sprite的碰撞判定，布林值代表要不要刪除
    hits = pygame.sprite.groupcollide(rocks,bullets,True,True)
    for hit in hits: #每一次碰撞後 
        random.choice(expls_sound).play()
        score += hit.radius #因為hits碰撞判定是rocks，所以可以用radius變數
        expl = Explosion(hit.rect.center,"large")
        all_sprites.add(expl)
        if random.random () > 0.95 : #randaom回傳0~1 如果大於 TRUE
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
            
        new_rock()
        # rock=Rock()  #產生一個Rock
        # all_sprites.add(rock) #加回群組才能做update與draw
        # rocks.add(rock) #新的石頭才能做判定
    
     #判斷飛船 石頭相撞
     #(sprite,gropus,dokill)) #第四個參數把判定改成圓形
    hits = pygame.sprite.spritecollide(player,rocks,True,pygame.sprite.collide_circle)
    for hit in hits : #撞到飛船的所有石頭
        new_rock()
        # rock=Rock()
        # all_sprites.add(rock)
        # rocks.add(rock)
        expl = Explosion(hit.rect.center,"small")
        all_sprites.add(expl)
        player.health -= hit.radius
        if player.health <= 0:
            death_expl = Explosion(player.rect.center,"player")
            all_sprites.add(death_expl)
            player_expl_sound.play()
            player.lives -= 1 
            player.health = 100
            player.hide() #隱藏飛船當復活時間

    #判斷飛船 寶物相撞
    hits = pygame.sprite.spritecollide(player,powers,True)
    for hit in hits:
        if hit.type == "shield":
            player.health += 20
            if player .health >100 :
                player.health =100
            shield_sound.play()
        if hit.type == "gun":
            player.gunup()
            gun_sound.play()


    if player.lives == 0 and not(death_expl.alive()):
        show_init = True
           

    #畫面顯示
    screen.fill((BLACK)) #(R,G,B) 0~255，調色盤
    screen.blit(background_img,(0,0)) #blit 點陣圖，(0,0)為畫的座標
    all_sprites.draw(screen) #在螢幕上畫上all_sprites
    draw_text(screen,str(score),25,WIDTH/2,10)
    draw_health(screen,player.health,5,18)
    draw_lives(screen,player.lives,player_mini_img,WIDTH-120, 15) #一個小圖示WIDTH 30像素，螢幕寬度往左100像素空間足夠
    pygame.display.update() #更新畫面
pygame.quit