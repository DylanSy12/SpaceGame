from cmu_graphics import *
app.background = 'black'
app.hazardLst = []
app.level = 1
app.setMaxShapeCount(100000)
app.sizeMulti = 2
app.width = 400*app.sizeMulti
app.height = 400*app.sizeMulti
class Projectile: 
    lst = []
    def __init__(self, rA, speed, power, harmShip, projectileType, *, piercing = 1): 
        self.rA = rA
        self.speed = speed
        self.previousSpeed = speed
        self.power = power
        self.piercing = piercing
        self.harmShip = harmShip
        self.type = projectileType
        Projectile.lst.append(self)
        if harmShip: 
            self.speed += app.score/1000
            app.hazardLst.append(self)
    # moves projectile
    def move(self): 
        if self.shape.visible: 
            self.shape.centerX, self.shape.centerY = getPointInDir(self.shape.centerX, self.shape.centerY, self.rA, self.speed)
            if not (self.shape.left > 400*app.sizeMulti or self.shape.right < 0 or self.shape.bottom < 0 or self.shape.top > 400*app.sizeMulti): 
                # collision
                if not self.harmShip: 
                    for e in EnemyShip.lst: 
                        if self.shape.hitsShape(e.shape) and e.hp>0: 
                            e.hp -= self.power*2-1
                            if self.piercing <= 1: 
                                self.shape.visible = False
                            else: 
                                self.piercing -= 1
                else: 
                    for s in Ship.lst: 
                        if self.shape.hitsShape(s.shape): 
                            if s.invTime <= 0: 
                                s.invTime = 1
                                s.shields -= self.power
                            if self.piercing <= 1: 
                                self.shape.visible = False
                            else: 
                                self.piercing -= 1
                if self.type != "ib": 
                    for a in Asteroid.lst: 
                        if self.shape.hitsShape(a.shape): 
                            if a.shape.radius-self.power*2*app.sizeMulti <= 4*app.sizeMulti: 
                                a.reset()
                            else: 
                                a.shape.radius -= self.power*2*app.sizeMulti
                            if self.piercing <= 1: 
                                self.shape.visible = False
                            else: 
                                self.piercing -= 1
                    for b in Bomb.lst: 
                        if self.shape.hitsShape(b.shape): 
                            if self.type == "l": 
                                if (not self.harmShip) or (self.harmShip and (not b.harmShip)): 
                                    if self.piercing <= 1: 
                                        self.shape.visible = False
                                    else: 
                                        self.piercing -= 1
                                    b.shape.visible = False
                            else: 
                                if self.harmShip != b.harmShip: 
                                    self.shape.visible = False
                                    b.shape.visible = False
            else: 
                # removes object if off screen
                removeObject(self)
        else: 
            # removes object, does effect
            removeObject(self)
            self.effect()
    def effect(self): 
        pass
class Laser(Projectile): 
    lst = []
    def __init__(self, sX, sY, laserFill, speed, power, *, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, rA = 90, harmShip = False, piercing = 1): 
        x2, y2 = getPointInDir(sX, sY, rA, length)
        self.shape = Line(sX, sY, x2, y2, fill = laserFill, lineWidth = lW)
        # calls Projectile constructor
        super().__init__(rA, speed, power, harmShip, "l", piercing = piercing)
        Laser.lst.append(self)
class Bomb(Projectile): 
    lst = []
    def __init__(
        self, sX, sY, speed, power, explosionPower, *, radius = 6*app.sizeMulti, 
        explosionSize = 35*app.sizeMulti, rA = 90, harmShip = False, bombFill = 'dimgray'
    ): 
        x2, y2 = getPointInDir(sX, sY, rA, radius)
        self.shape = Circle(x2, y2, radius, fill = bombFill)
        self.bombFill = bombFill
        self.explosionPower = explosionPower
        self.explosionSize = explosionSize
        # calls Projectile constructor
        super().__init__(rA, speed, power, harmShip, "b")
        Bomb.lst.append(self)
    # creates an explosion based on the Bomb's stats
    def effect(self): 
        Explosion(self.shape.centerX, self.shape.centerY, self.explosionPower, size = self.explosionSize)
class ClusterBomb(Bomb): 
    def __init__(
        self, sX, sY, speed, power, *, radius = 6*app.sizeMulti, rA = 90, harmShip = False, numBombs = 3, clusterBombExplosionSize = 15*app.sizeMulti, 
        bombFill = 'dimgray', clusterBombExplosionDamage = 2, recursions = 0
    ): 
        self.numBombs = numBombs
        self.clusterBombExplosionSize = clusterBombExplosionSize
        self.clusterBombExplosionDamage = clusterBombExplosionDamage
        self.recursions = recursions
        # calls Bomb constructor
        super().__init__(
            sX, sY, speed, power, 0, radius = radius, explosionSize = 1*app.sizeMulti, 
            rA = rA, harmShip = harmShip, bombFill = bombFill
        )
    # spawns bombs or more cluster bombs depending on how many rcrsns are left
    def effect(self): 
        if self.recursions > 0: 
            for i in range(self.numBombs): 
                rotate = randrange(0, 360)
                if self.numBombs-1 < 3: 
                    self.numBombs = 4
                sX, sY = getPointInDir(self.shape.centerX, self.shape.centerY, rotate, randrange(5, 15))
                ClusterBomb(
                    sX, sY, int(self.speed/2)+1*app.sizeMulti, self.power*0.75, radius = int(self.shape.radius/2)+1*app.sizeMulti, 
                    rA = rotate, harmShip = self.harmShip, numBombs = self.numBombs-1, recursions = self.recursions-1, 
                    bombFill = self.bombFill, clusterBombExplosionSize = int(self.clusterBombExplosionSize*0.875)+1*app.sizeMulti, 
                    clusterBombExplosionDamage = self.clusterBombExplosionDamage
                )
        else: 
            for i in range(self.numBombs): 
                rotate = randrange(0, 360)
                sX, sY = getPointInDir(self.shape.centerX, self.shape.centerY, rotate, randrange(5, 15)*app.sizeMulti)
                Bomb(
                    sX, sY, int(self.speed/2)+2.5*app.sizeMulti, self.power*0.75, self.clusterBombExplosionDamage, bombFill = self.bombFill, 
                    radius = self.shape.radius/2, rA = rotate, explosionSize = self.clusterBombExplosionSize, harmShip = self.harmShip
                )
class Explosion: 
    lst = []
    def __init__(self, cX, cY, power, *, size = 15*app.sizeMulti): 
        self.shape = Circle(cX, cY, 1*app.sizeMulti, fill = gradient('yellow', 'gold', 'orange', 'orangered', 'red', 'crimson'))
        self.power = power
        self.size = size
        Explosion.lst.append(self)
        app.hazardLst.append(self)
    def explode(self): 
        if self.shape.radius < self.size: 
            # expands Explosion, does collision
            self.shape.radius += randrange(1, 4)*app.sizeMulti
            for e in EnemyShip.lst: 
                if self.shape.hitsShape(e.shape): 
                    e.hp -= self.power*1.5
            for s in Ship.lst: 
                if self.shape.hitsShape(s.shape) and s.invTime <= 0: 
                    s.shields -= self.power
                    s.invTime = 3
            for a in Asteroid.lst: 
                if self.shape.hitsShape(a.shape): 
                    if a.shape.radius-self.power*2*app.sizeMulti <= 4*app.sizeMulti: 
                        a.reset()
                    else: 
                        a.shape.radius -= self.power*2*app.sizeMulti
            for b in Bomb.lst: 
                if self.shape.hitsShape(b.shape): 
                    b.shape.visible = False
        else: 
            # removes Explosion
            removeObject(self)    
class IonBlast(Projectile): 
    lst = []
    def __init__(
        self, sX, sY, ionFill, speed, *, empSize = 15*app.sizeMulti, lW = 2*app.sizeMulti, 
        length = 5*app.sizeMulti, rA = 90, harmShip = False, empDuration = 60
    ): 
        x2, y2 = getPointInDir(sX, sY, rA, length)
        self.shape = Line(sX, sY, x2, y2, fill = ionFill, lineWidth = lW)
        self.empSize = empSize
        self.empDuration = empDuration
        # calls Projectile constructor
        super().__init__(rA, speed, 0, harmShip, "ib")
        IonBlast.lst.append(self)
    # creates EMP depending on the IonBlast's stats
    def effect(self): 
        EMP(self.shape.right, self.shape.centerY, size = self.empSize, duration = self.empDuration)
class EMP: 
    lst = []
    def __init__(self, cX, cY, *, size = 15*app.sizeMulti, duration = 60): 
        self.shape = Circle(cX, cY, 1*app.sizeMulti, fill = gradient('blue', 'navy', 'mediumvioletred', 'magenta', 'purple'))
        self.size = size
        self.duration = duration
        EMP.lst.append(self)
        app.hazardLst.append(self)
    def stun(self): 
        if self.shape.radius <= self.size: 
            # expands EMP, stuns hit ships
            self.shape.radius += randrange(3, 11)*app.sizeMulti
            for e in EnemyShip.lst: 
                if self.shape.hitsShape(e.shape): 
                    e.speed = 0
                    e.cooldown = self.duration*2
            for s in Ship.lst: 
                if self.shape.hitsShape(s.shape): 
                    s.stunned = True
        elif self.duration > 0: 
            # ticks down duration
            self.shape.visible = False
            self.duration -= 1
        else: 
            # removes EMP
            self.shape.visible = True
            for e in EnemyShip.lst: 
                if self.shape.hitsShape(e.shape): 
                    e.speed = e.previousSpeed
            for s in Ship.lst: 
                if self.shape.hitsShape(s.shape): 
                    s.stunned = False
            removeObject(self)
class EnemyShip: 
    lst = []
    def __init__(self, cY, speed, hp, score, cooldownMax, type, destroyerSpawned): 
        self.shape.centerY = cY
        self.speed = speed+app.score/1000
        self.hp = hp+int(app.score/100)+app.enemyHPMod
        self.cooldown = 10
        self.cooldownMax = cooldownMax+app.enemyCooldownMod
        self.direction = 0
        self.deployCooldown = 150
        self.score = score
        self.type = type
        self.destroyerSpawned = destroyerSpawned
        self.previousSpeed = speed+app.score/1000
        EnemyShip.lst.append(self)
        app.hazardLst.append(self)
    # moves EnemyShip
    def move(self): 
        if self.hp > 0: 
            # tracks nearest player ship
            shipDistance = 1000000000
            shipY = 0
            for ship in Ship.lst: 
                if ship.shape.visible: 
                    if distance(self.shape.centerX, self.shape.centerY, ship.shape.centerX, ship.shape.centerY) < shipDistance: 
                        shipDistance = distance(self.shape.centerX, self.shape.centerY, ship.shape.centerX, ship.shape.centerY)
                        shipY = ship.shape.centerY
            if shipY < self.shape.centerY: 
                self.direction = -1
            elif shipY > self.shape.centerY: 
                self.direction = 1
            else: 
                self.direction = 0
            # shoots
            self.shape.centerY += self.speed*self.direction
            if self.cooldown <= 0: 
                self.cooldown = self.cooldownMax
                self.shoot()
            else: 
                self.cooldown -= 1
            # if the EnemyShip is a StarDestroyer, spawns more enemies
            if self.type == "sd": 
                if self.deployCooldown <= 0: 
                    self.deployCooldown = 150+app.enemyCooldownMod
                    for i in range(randrange(0, 5)): 
                        TieFighter(cY = self.shape.centerY+randrange(-30, 31)*app.sizeMulti, destroyerSpawned = True)
                    for i in range(randrange(0, 3)): 
                        TieBomber(cY = self.shape.centerY+randrange(-30, 31)*app.sizeMulti, destroyerSpawned = True)
                else: 
                    self.deployCooldown -= 1
        else: 
            # removes EnemyShip
            removeObject(self)
            if self.type == "tf": 
                Explosion(self.shape.centerX, self.shape.centerY, 0.5+app.enemyDMGMod)
            elif self.type == "tb": 
                Explosion(self.shape.centerX, self.shape.centerY, 1+app.enemyDMGMod, size = 25*app.sizeMulti)
            else: 
                Explosion(self.shape.centerX, self.shape.centerY, 2+app.enemyDMGMod, size = 35*app.sizeMulti)
            # adds to score, potentially adds a new Asteroid
            app.score += self.score
            i = 0
            while i < self.score: 
                if app.score%app.asteroidRate == i and app.score != 0 and len(Asteroid.lst) < app.asteroidCap: 
                    Asteroid()
                i += 1
            # spawns upgrades
            if app.numPlayers == 1: 
                if not self.destroyerSpawned: 
                    if self.type == "tf": 
                        Level.levelLst[app.level].tFDestroyed += 1
                        if randrange(1, 16) == 1: 
                            upgradeSpawn(self.shape.centerX, self.shape.centerY)
                    elif self.type == "tb": 
                        Level.levelLst[app.level].tBDestroyed += 1
                        for i in range(randrange(0, 2)): 
                            if randrange(1, 11) == 1: 
                                upgradeSpawn(self.shape.centerX, self.shape.centerY)
                if self.type == "sd": 
                    Level.levelLst[app.level].sDDestroyed += 1
                    for i in range(randrange(0, 2)+3): 
                        if randrange(1, 11) == 1: 
                            upgradeSpawn(self.shape.centerX, self.shape.centerY)
class TieFighter(EnemyShip): 
    lst = []
    def __init__(self, cY, *, destroyerSpawned = False): 
        self.shape = Group(
            RegularPolygon(380, cY, 20, 6, border = 'gray', rotateAngle = 90), 
            RegularPolygon(380, cY, 5, 6, border = 'dimgray', rotateAngle = 90)
        )
        for i in range(6): 
            x1, y1 = getPointInDir(380, cY, 30+60*i, 5)
            x2, y2 = getPointInDir(380, cY, 30+60*i, 20)
            self.shape.add(Line(x1, y1, x2, y2, fill = 'gray'))
        self.shape.width *= (4/5)*app.sizeMulti
        self.shape.height *= (4/5)*app.sizeMulti
        self.shape.centerX = 380*app.sizeMulti
        # calls EnemyShip constructor
        super().__init__(cY, 1*app.sizeMulti, 15, 2, 35, "tf", destroyerSpawned)
        TieFighter.lst.append(self)
    # shoots Laser
    def shoot(self): 
        Laser(
            self.shape.left, self.shape.centerY, 'limegreen', 4.5*app.sizeMulti, 1+app.enemyDMGMod, 
            harmShip = True, lW = 3.5*app.sizeMulti, rA = 270, length = 7.5*app.sizeMulti, piercing = 2
        )
class TieBomber(EnemyShip): 
    lst = []
    def __init__(self, cY, *, destroyerSpawned = False): 
        self.shape = Group(
            Line(357.5, cY, 402.5, cY, lineWidth = 20, fill = 'gray'), 
            RegularPolygon(380, cY, 20, 6, border = 'gray', rotateAngle = 90), 
            RegularPolygon(380, cY, 5, 6, border = 'dimgray', rotateAngle = 90)
        )
        for i in range(6): 
            x1, y1 = getPointInDir(380, cY, 30+60*i, 5)
            x2, y2 = getPointInDir(380, cY, 30+60*i, 20)
            self.shape.add(Line(x1, y1, x2, y2, fill = 'gray'))
        self.shape.width *= (4/5)*app.sizeMulti
        self.shape.height *= (4/5)*app.sizeMulti
        self.shape.centerX = 380*app.sizeMulti
        # calls EnemyShip constructor
        super().__init__(cY, 0.75*app.sizeMulti, 30, 4, 60, "tb", destroyerSpawned)
        TieBomber.lst.append(self)
    # shoots Bomb
    def shoot(self): 
        Bomb(
            self.shape.left, self.shape.centerY, 3*app.sizeMulti, 4+app.enemyDMGMod, 1, 
            radius = 7.5*app.sizeMulti, explosionSize = 15*app.sizeMulti, rA = 270, harmShip = True
        )
class StarDestroyer(EnemyShip): 
    lst = []
    def __init__(self, cY): 
        self.shape = Group(
            Line(390, cY, 397.5, cY, lineWidth = 10, fill = 'dimgray'), 
            Line(397.5, cY-5, 397.5, cY+5, fill = 'cyan'), 
            Line(387.5, cY-12.5, 387.5, cY, fill = 'dimgray', lineWidth = 6), 
            Line(382.5, cY-15, 392.5, cY-15, fill = 'gray', lineWidth = 5), 
            Circle(387.5, cY-20, 2.5, fill = 'gray'), 
            Polygon(395, cY-7.5, 395, cY+10, 385, cY+10, 310, cY+6.5, 310, cY, 385, cY-7.5, fill = 'gray')
        )
        self.shape.width *= 1.25*app.sizeMulti
        self.shape.height *= 1.25*app.sizeMulti
        self.shape.right = 397.5*app.sizeMulti
        # calls EnemyShip constructor
        super().__init__(cY, 0.75*app.sizeMulti, 60, 10, 105, "sd", False)
        StarDestroyer.lst.append(self)
    # shoots Laser
    def shoot(self): 
        Laser(
            self.shape.centerX+15*app.sizeMulti, self.shape.centerY-1*app.sizeMulti, 'limegreen', 4, 5+app.enemyDMGMod, 
            harmShip = True, lW = 4*app.sizeMulti, rA = 270, length = 10*app.sizeMulti, piercing = 3
        )
class Asteroid: 
    lst = []
    def __init__(self): 
        self.shape = RegularPolygon(
            430*app.sizeMulti+10, randrange(20, 380)*app.sizeMulti, randrange(10, 30)*app.sizeMulti, 7, 
            fill = gradient('dimgray', 'grey', 'darkgray', 'grey', 'dimgray', start = 'left')
        )
        self.speed = 6*app.sizeMulti-self.shape.radius/10
        Asteroid.lst.append(self)
        app.hazardLst.append(self)
    # moves asteroid, does collision, resets Asteroid if off screen
    def move(self): 
        self.speed = 6*app.sizeMulti-self.shape.radius/10+app.score/1000*app.sizeMulti
        if self.shape.right > 0: 
            self.shape.centerX -= self.speed
            self.shape.rotateAngle += 1
        else: 
            self.reset()
        for ship in Ship.lst: 
            if self.shape.hitsShape(ship.shape): 
                if ship.invTime <= 0: 
                    ship.shields -= int(self.shape.radius/10/app.sizeMulti)+1
                    ship.invTime = 1
                self.reset()
    # resets Asteroid
    def reset(self): 
        # resets asteroids, gives them new size and speed
        self.shape.left = (375+randrange(50, 200))*app.sizeMulti
        self.shape.centerY = randrange(20, 380)*app.sizeMulti
        self.shape.radius = (randrange(10, 30)+app.score/100)*app.sizeMulti
        if self.shape.radius > (100+app.asteroidSizeMod)*app.sizeMulti: 
            self.shape.radius = (100+app.asteroidSizeMod)*app.sizeMulti
        self.speed = 6*app.sizeMulti-self.shape.radius/10+app.score/1000*app.sizeMulti
        # adds a new asteroid every app.asteroidRate score
        if app.score%app.asteroidRate == 0 and app.score != 0 and len(Asteroid.lst) < app.asteroidCap: 
            Asteroid()
        if app.numPlayers == 1: 
            Level.levelLst[app.level].asteroidsDestroyed += 1
        app.score += 1
class Ship: 
    lst = []
    def __init__(self, speed, shotCooldown, hp, shields, shieldCooldown, upKey, downKey, rightKey, leftKey, shootKey, abilityKey): 
        self.speed = speed
        self.shotCooldown = 0
        self.shotCooldownMax = shotCooldown
        self.hp = hp
        self.hpMax = hp
        self.shields = shields
        self.shieldsMax = shields
        self.shieldCooldown = shieldCooldown
        self.shieldCooldownMax = shieldCooldown
        self.upKey = upKey
        self.downKey = downKey
        self.rightKey = rightKey
        self.leftKey = leftKey
        self.shootKey = shootKey
        self.abilityKey = abilityKey
        self.abilityCooldown = 0
        self.abilityTimer = 0
        self.stunned = False
        self.invTime = 30
        # information (hp, shield, shotCooldown, abilityCooldown) bars (lets the player know roughly what these values are at)
        self.healthBarBack = Line(
            self.shape.centerX-40*app.sizeMulti, self.shape.bottom+1.25*app.sizeMulti, self.shape.centerX+40*app.sizeMulti, 
            self.shape.bottom+1.25*app.sizeMulti, fill =  'seagreen', lineWidth = 2.5*app.sizeMulti
        )
        self.shieldBarBack = Line(
            self.shape.centerX-40*app.sizeMulti, self.shape.bottom+5*app.sizeMulti, self.shape.centerX+40*app.sizeMulti, 
            self.shape.bottom+5*app.sizeMulti, fill = 'cadetblue', lineWidth = 2.5*app.sizeMulti
        )
        self.shotCooldownBarBack = Line(
            self.shape.centerX-40*app.sizeMulti, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX, 
            self.shape.bottom+8.75*app.sizeMulti, fill = 'firebrick', lineWidth = 2.5*app.sizeMulti
        )
        self.abilityBarBack = Line(
            self.shape.centerX, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX+40*app.sizeMulti, 
            self.shape.bottom+8.75*app.sizeMulti, fill = 'darkkhaki', lineWidth = 2.5*app.sizeMulti
        )
        self.hpBar = Line(
            self.shape.centerX-40*app.sizeMulti, self.shape.bottom+1.25*app.sizeMulti, self.shape.centerX+40*app.sizeMulti, 
            self.shape.bottom+1.25*app.sizeMulti, fill = 'limegreen', lineWidth = 2.5*app.sizeMulti
        )
        self.shieldBar = Line(
            self.shape.centerX-40*app.sizeMulti, self.shape.bottom+5*app.sizeMulti, self.shape.centerX+40*app.sizeMulti, 
            self.shape.bottom+5*app.sizeMulti, fill = 'cyan', lineWidth = 2.5*app.sizeMulti
        )
        self.shieldCooldownBar = Line(
            self.shape.centerX-40*app.sizeMulti, self.shape.bottom+5*app.sizeMulti, self.shape.centerX+40*app.sizeMulti, 
            self.shape.bottom+5*app.sizeMulti, fill = 'lightcyan', lineWidth = 1.25*app.sizeMulti
        )
        self.shotCooldownBar = Line(
            self.shape.centerX-40*app.sizeMulti, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX, 
            self.shape.bottom+8.75*app.sizeMulti, fill = 'red', lineWidth = 2.5*app.sizeMulti
        )
        self.abilityBar = Line(
            self.shape.centerX, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX+40*app.sizeMulti, 
            self.shape.bottom+8.75*app.sizeMulti, fill = 'gold', lineWidth = 2.5*app.sizeMulti
        )
        self.barGroup = Group(
            self.healthBarBack, self.shieldBarBack, self.shotCooldownBarBack, self.abilityBarBack, self.hpBar, 
            self.shieldBar, self.shieldCooldownBar, self.shotCooldownBar, self.abilityBar
        )
        Ship.lst.append(self)
    def shieldRegen(self): 
        if self.shields < self.shieldsMax: 
            if self.shieldCooldown <= 0: 
                self.shieldCooldown = self.shieldCooldownMax
                self.shields += 1
            else: 
                self.shieldCooldown -= 1
    def onStep(self): 
        if self.hp > 0: 
            self.invTime -= 1
            # updates hp
            if self.shields < 0: 
                self.hp += self.shields
                self.shields = 0
            if not self.stunned: 
                # regens shield (or hp if the ship is the Falcon and has hp regen Enabled)
                if self.type == "F" and self.hp < self.hpMax: 
                    if self.healthRegenEnabled: 
                        if self.shieldCooldown <= 0: 
                            self.shieldCooldown = self.shieldCooldownMax
                            self.hp += 1
                        else: 
                            self.shieldCooldown -= 1
                    else: 
                        self.shieldRegen() 
                else: 
                    self.shieldRegen()
                if self.abilityTimer <= 0 or self.moveWhileAbility: 
                    # updates shotCooldown(Bar)
                    if self.shotCooldown > 0: 
                        self.shotCooldown -= 1
                        self.shotCooldownBar.fill = 'crimson'
                        self.shotCooldownBar.lineWidth = 1.25*app.sizeMulti
                    else: 
                        self.shotCooldownBar.fill = 'red'
                        self.shotCooldownBar.lineWidth = 2.5*app.sizeMulti
                    # checks if certain keys are pressed
                    # moves Ship
                    if self.upKey in app.keys or (app.numPlayers == 1 and "w" in app.keys): 
                        if self.shape.top-self.speed < 0: 
                            self.shape.top = 0
                        else: 
                            self.shape.centerY -= self.speed
                        self.keysLst.append(self.upKey)
                    elif self.downKey in app.keys or (app.numPlayers == 1 and "s" in app.keys): 
                        if self.shape.bottom+self.speed > 400*app.sizeMulti: 
                            self.shape.bottom = 400*app.sizeMulti
                        else: 
                            self.shape.centerY += self.speed
                        self.keysLst.append(self.downKey)
                    if self.leftKey in app.keys or (app.numPlayers == 1 and "a" in app.keys): 
                        if self.shape.left-self.speed < 0: 
                            self.shape.left = 0
                        else: 
                            self.shape.centerX -= self.speed
                        self.keysLst.append(self.leftKey)
                    elif self.rightKey in app.keys or (app.numPlayers == 1 and "d" in app.keys): 
                        if self.shape.right+self.speed > 400*app.sizeMulti: 
                            self.shape.right = 400*app.sizeMulti
                        else: 
                            self.shape.centerX += self.speed
                        self.keysLst.append(self.rightKey)
                    # calls shoot function (each Ship has a unique shot pattern)
                    if self.shootKey in app.keys and self.shotCooldown <= 0: 
                        app.keys.remove(self.shootKey)
                        shoot = True
                        if self.abilityTimer > 0: 
                            if self.type == "f": 
                                if self.autoAimEnabled: 
                                    shoot = False
                            elif self.type == "x": 
                                if self.dashEnabled: 
                                    shoot = False
                        if shoot: 
                            self.shotCooldown = self.shotCooldownMax
                            self.shoot()
                # calls ability function (each Ship has unique abilities)
                self.ability()
            # updates information bars
            self.barGroup.centerX = self.shape.centerX
            self.barGroup.centerY = self.shape.bottom+7.5
            self.hpBar.x2 = self.shape.centerX+(-40+self.hp*80/self.hpMax)*app.sizeMulti
            self.shieldBar.x2 = self.shape.centerX+(-40+self.shields*(80/self.shieldsMax))*app.sizeMulti
            if self.shieldCooldownMax > 0: 
                self.shieldCooldownBar.x2 = self.shape.centerX+(40-self.shieldCooldown*80/self.shieldCooldownMax)*app.sizeMulti
            if self.shotCooldownMax > 0: 
                self.shotCooldownBar.x2 = self.shape.centerX-self.shotCooldown*(40*app.sizeMulti/self.shotCooldownMax)
            self.shape.toFront()
            self.barGroup.toFront()
        else: 
            # removes Ship
            removeObject(self)
            self.barGroup.visible = False
class XWing(Ship): 
    # ability: dash
    boostLst = []
    for i in range(10): 
        boostLst.append(0)
    abilityBoostLst = []
    for i in range(5): 
        abilityBoostLst.append(0)
    abilityBoostNameLst = ["Dash Ability Cooldown" , "Support Ability Cooldown", "Support Ability Duration", "Support Strength", "# of Support Ships"]
    def __init__(self, cX, cY, upKey, downKey, rightKey, leftKey, shootKey, abilityKey, *, dashEnabled = False, supportEnabled = False): 
        self.shape = Group(
            Polygon(
                300, 198, 263, 184, 211, 176, 175, 160, 137, 146, 97, 148, 78, 164, 34, 172, 38, 204, 299, 204, 
                fill = gradient('grey', 'firebrick', 'grey', 'firebrick', 'grey', 'grey', 'grey', 'dimGrey', 'dimGrey', start = 'right')
            ), 
            Polygon(263, 183, 123, 172, 123, 147, 137, 146, 175, 154, 211, 176, fill = gradient('grey', 'black', 'grey', 'grey', 'grey', start = 'left')), 
            Polygon(
                76, 164, 26, 165, 24, 170, 26, 181, 74, 181, 75, 175, 139, 175, 139, 164, 
                fill = gradient('dimGrey', 'dimGrey', 'dimGrey', 'black', start = 'right'), 
                border = gradient('grey', 'dimGrey', start = 'left')
            ), 
            Polygon(
                76, 190, 26, 191, 24, 96, 26, 207, 74, 207, 75, 201, 139, 201, 139, 190, 
                fill = gradient('dimGrey', 'dimGrey', 'dimGrey', 'black', start = 'right'), 
                border = gradient('grey', 'dimGrey', start = 'left')
            ), 
            Line(65, 114, 130, 114, fill = 'dimGrey', lineWidth = 8), 
            Line(130, 114, 155, 114, lineWidth = 5, fill = 'dimGrey'), 
            Line(155, 114, 193, 114, lineWidth = 3, fill = 'dimGrey'), 
            Line(65, 251, 130, 251, fill = 'dimGrey', lineWidth = 8), 
            Line(130, 251, 155, 251, lineWidth = 5, fill = 'dimGrey'), 
            Line(155, 251, 193, 251, lineWidth = 3, fill = 'dimGrey'), 
            Polygon(93, 255, 116, 255, 133, 190, 72, 190, fill = gradient('gainsboro', 'dimGrey', start = 'bottom')), 
            Polygon(72, 175, 93, 110, 116, 110, 133, 175, fill = gradient('gainsboro', 'dimGrey', start = 'top')), 
            Polygon(72, 175, 72, 190, 133, 190, 133, 175, fill = gradient('dimGrey', 'black', 'dimGrey', start = 'top')), 
            Polygon(263, 184, 265, 189, 267, 194, 265, 200, 263, 204, 299, 204, 300, 198, fill = 'white')
        )
        self.shape.width = 70*app.sizeMulti
        self.shape.height = 40*app.sizeMulti
        self.shape.centerX = cX
        self.shape.centerY = cY
        self.dashEnabled = dashEnabled
        self.supportEnabled = supportEnabled
        if dashEnabled: 
            self.moveWhileAbility = False
            self.abilityTimerMax = 15
        else: 
            self.moveWhileAbility = True
        self.keysLst = [rightKey]
        self.type = "X"
        # calls Ship constructor with different values depending on if the player chose multiplayer or not
        if app.numPlayers == 1: 
            if dashEnabled: 
                self.abilityCooldownMax = 61-15*XWing.abilityBoostLst[0]
            elif supportEnabled: 
                self.abilityCooldownMax = 151-15*XWing.abilityBoostLst[1]
                self.abilityTimerMax = 180+5*XWing.abilityBoostLst[2]
            self.dashSpeed = (7.5+XWing.boostLst[0]*0.01)*app.sizeMulti
            self.numOfSupports = 2+int(XWing.abilityBoostLst[4]/5)
            super().__init__(
                4.5*app.sizeMulti+(XWing.boostLst[0]*0.25)*app.sizeMulti, 0, 3+XWing.boostLst[2], 3+XWing.boostLst[3], 
                210-(XWing.boostLst[4]*15), upKey, downKey, rightKey, leftKey, shootKey, abilityKey
            )
        else: 
            if dashEnabled: 
                self.abilityCooldownMax = 61
            elif supportEnabled: 
                self.abilityCooldownMax = 151
                self.abilityTimerMax = 180
            self.dashSpeed = 7.5*app.sizeMulti
            self.numOfSupports = 2
            super().__init__(4.5*app.sizeMulti, 0, 3, 3, 210, upKey, downKey, rightKey, leftKey, shootKey, abilityKey)
    # shoots Lasers
    def shoot(self): 
        if app.numPlayers == 1: 
            Laser(
                self.shape.right-27*app.sizeMulti, self.shape.centerY-16*app.sizeMulti, 'red', (6+(XWing.boostLst[6]*0.25))*app.sizeMulti, 1.5+(XWing.boostLst[5]*0.25), 
                lW = (2+(XWing.boostLst[8]*0.25))*app.sizeMulti, length = (5+(XWing.boostLst[9]*0.5))*app.sizeMulti, piercing = 2+XWing.boostLst[7]
            )
            Laser(
                self.shape.right-27*app.sizeMulti, self.shape.centerY+19*app.sizeMulti, 'red', (6+(XWing.boostLst[6]*0.25))*app.sizeMulti, 1.5+(XWing.boostLst[5]*0.25), 
                lW = (2+(XWing.boostLst[8]*0.25))*app.sizeMulti, length = (5+(XWing.boostLst[9]*0.5))*app.sizeMulti, piercing = 2+XWing.boostLst[7]
            )
        else: 
            Laser(self.shape.right-27*app.sizeMulti, self.shape.centerY-16*app.sizeMulti, 'red', 6*app.sizeMulti, 1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2)
            Laser(self.shape.right-27*app.sizeMulti, self.shape.centerY+19*app.sizeMulti, 'red', 6*app.sizeMulti, 1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2)
    # defines what the XWing's abilities do
    def ability(self): 
        if self.abilityKey in app.keys and self.abilityCooldown <= 0: 
            self.abilityCooldown = self.abilityCooldownMax
            app.keys.remove(self.abilityKey)
            if self.supportEnabled: 
                if app.numPlayers == 1: 
                    for i in range(10): 
                        temp = SupportShip.boostLst[i]
                        SupportShip.boostLst[i] = XWing.boostLst[i]*((1+XWing.abilityBoostLst[3])/100)
                        XWing.boostLst[i] = temp
                for i in range(self.numOfSupports): 
                    SupportShip(randrange(0, 401), duration = self.abilityTimerMax)
                if app.numPlayers == 1: 
                    for i in range(10): 
                        temp = int(SupportShip.boostLst[i]/((1+XWing.abilityBoostLst[3])/100))
                        SupportShip.boostLst[i] = XWing.boostLst[i]
                        XWing.boostLst[i] = temp
            self.abilityTimer = self.abilityTimerMax
        elif self.abilityTimer > 0: 
            # dash ability
            if self.dashEnabled: 
                # moves XWing
                if self.keysLst[len(self.keysLst)-1] == self.upKey: 
                    self.shape.centerY -= self.dashSpeed
                elif self.keysLst[len(self.keysLst)-1] == self.downKey: 
                    self.shape.centerY += self.dashSpeed
                elif self.keysLst[len(self.keysLst)-1] == self.leftKey: 
                    self.shape.centerX -= self.dashSpeed
                elif self.keysLst[len(self.keysLst)-1] == self.rightKey: 
                    self.shape.centerX += self.dashSpeed
                if self.shape.top < 0: 
                    self.shape.top = 0
                elif self.shape.bottom > 400*app.sizeMulti: 
                    self.shape.bottom = 400*app.sizeMulti
                if self.shape.left < 0: 
                    self.shape.left = 0
                elif self.shape.right > 400*app.sizeMulti: 
                    self.shape.right = 400*app.sizeMulti
            if self.supportEnabled: 
                if len(SupportShip.lst) == 0: 
                    self.abilityTimer = 1
            # updates ability bar, updates timers
            self.abilityTimer -= 1
            self.abilityBar.fill = 'yellow'
            self.abilityBar.x2 = self.shape.centerX+self.abilityTimer*(40*app.sizeMulti/self.abilityTimerMax)
        elif self.abilityCooldown > 0: 
            self.abilityCooldown -= 1
            self.abilityBar.fill = 'palegoldenrod'
            self.abilityBar.x2 = self.shape.centerX+(40-self.abilityCooldown*40/self.abilityCooldownMax)*app.sizeMulti
            self.abilityBar.lineWidth = 1.25*app.sizeMulti
        else: 
            self.abilityBar.fill = 'gold'
            self.abilityBar.lineWidth = 2.5*app.sizeMulti
class YWing(Ship): 
    # ability: bomb, ion cannon
    boostLst = []
    for i in range(10): 
        boostLst.append(0)
    abilityBoostLst = []
    for i in range(10): 
        abilityBoostLst.append(0)
    abilityBoostNameLst = [
        "Ability Cooldown", "Bomb Charges", "Bomb Size", "Bomb Radius", "EMP Charges", "EMP Radius", "EMP Duration", "Cluster Bomb Charges", 
        "Cluster Bomb Fragments", "Cluster Bomb Recursions"
    ]
    def __init__(self, cX, cY, upKey, downKey, rightKey, leftKey, shootKey, abilityKey, *, bomb = False, emp = False, cluster = False): 
        self.shape = Group(
            Polygon(118, 193, 248, 193, 258, 187, 294, 187, 294, 185, 310, 185, 310, 183, 294, 183, 293, 181, 269, 175, 257, 167, 217, 167, 216, 176, 118, 176, fill = 'dimGrey'), 
            Rect(33, 178, 85, 19, fill = None, border = 'grey'), 
            Polygon(100, 185, 100, 190, 112, 197, 170, 197, 174, 193, 175, 188, 175, 186, 175, 186, 174, 182, 173, 181, 167, 178, 110, 178, fill = 'grey'), 
            Polygon(217, 167, 257, 167, 269, 176, 259, 176, 216, 176, fill = 'steelBlue'), 
            Polygon(247, 169, 255, 169, 260, 174, 247, 174, fill = gradient('grey', 'grey', 'cornflowerBlue', start = 'bottom-left')), 
            Polygon(235, 170, 223, 170, 222, 174, 235, 174, fill = gradient('grey', 'grey', 'cornflowerBlue', start = 'bottom-left'))
        )
        self.shape.width = 84*app.sizeMulti
        self.shape.height = 15*app.sizeMulti
        self.shape.centerX = cX
        self.shape.centerY = cY
        self.abilityTimerMax = 1
        self.keysLst = []
        self.bombEnabled = bomb
        self.empEnabled = emp
        self.clusterEnabled = cluster
        self.moveWhileAbility = True
        self.type = "Y"
        # calls Ship constructor with different values depending on if the player chose multiplayer or not
        if app.numPlayers == 1: 
            self.bombCharges = 3+YWing.abilityBoostLst[1]
            self.bombSize = 4-YWing.abilityBoostLst[2]*0.25
            self.empCharges = 3+YWing.abilityBoostLst[4]
            self.clusterCharges = 3+YWing.abilityBoostLst[7]
            self.abilityCooldownMax = 91-15*YWing.abilityBoostLst[0]
            super().__init__(
                2.5*app.sizeMulti+(YWing.boostLst[0]*0.25)*app.sizeMulti, 20-int(YWing.boostLst[1]/2), 5+YWing.boostLst[2], 
                4+YWing.boostLst[3], 450-(YWing.boostLst[4]*15), upKey, downKey, rightKey, leftKey, shootKey, abilityKey
            )
        else: 
            self.bombCharges = 3
            self.clusterCharges = 3
            self.abilityCooldownMax = 91
            self.empCharges = 3
            super().__init__(2.5*app.sizeMulti, 20, 5, 4, 450, upKey, downKey, rightKey, leftKey, shootKey, abilityKey)
        self.bombChargesMax = self.bombCharges
        self.empChargesMax = self.empCharges
        self.clusterChargesMax = self.clusterCharges
    # shoots Laser
    def shoot(self): 
        if app.numPlayers == 1: 
            Laser(
                self.shape.right, self.shape.centerY, 'green', (4.25+(YWing.boostLst[6]*0.25))*app.sizeMulti, 7.5+(YWing.boostLst[5]*0.25), 
                lW = (3+(YWing.boostLst[8]*0.25))*app.sizeMulti, length = (7.5+(YWing.boostLst[9]*0.5))*app.sizeMulti, 
                piercing = 2+YWing.boostLst[7]
            )
        else: 
            Laser(self.shape.right, self.shape.centerY, 'green', 4.25*app.sizeMulti, 7.5 , lW = 3*app.sizeMulti, length = 7.5*app.sizeMulti, piercing = 2)
    # defines what the YWing's abilities do
    def ability(self): 
        if self.abilityKey in app.keys: 
            # shoots projectile depending on what abilities are Enabled, lowers the amount of Chrgs left
            # shoots Bomb if bomb is Enabled
            if self.bombEnabled and self.bombCharges > 0: 
                if app.numPlayers == 1: 
                    Bomb(
                        self.shape.right, self.shape.centerY, (3.5+YWing.boostLst[6]*0.1)*app.sizeMulti, 15+YWing.boostLst[5]*0.25, 2+YWing.boostLst[5]*0.05, 
                        radius = self.bombSize*app.sizeMulti, explosionSize = 25*app.sizeMulti+int(YWing.abilityBoostLst[3]*0.5)*app.sizeMulti, rA = 90
                    )
                else: 
                    Bomb(self.shape.right, self.shape.centerY, 3.5*app.sizeMulti, 15, 2, radius = 4*app.sizeMulti, explosionSize = 25*app.sizeMulti, rA = 90)
                self.bombCharges -= 1
            # shoots IonBlast if emp is Enabled
            if self.empEnabled and self.empCharges > 0: 
                if app.numPlayers == 1: 
                    IonBlast(
                        self.shape.right, self.shape.centerY, 'magenta', (5+(YWing.boostLst[6]*0.25))*app.sizeMulti, 
                        empSize = (30+int(YWing.abilityBoostLst[5]*0.1))*app.sizeMulti, lW = 4*app.sizeMulti, 
                        length = 7*app.sizeMulti, empDuration = 120+YWing.abilityBoostLst[6]
                    )
                else: 
                    IonBlast(
                        self.shape.right, self.shape.centerY, 'magenta', 5*app.sizeMulti, empSize = 30*app.sizeMulti, 
                        lW = 4*app.sizeMulti, length = 7*app.sizeMulti, empDuration = 120
                    )
                self.empCharges -= 1
            # shoots ClusterBomb if cluster is enabled
            if self.clusterEnabled and self.clusterCharges > 0: 
                if app.numPlayers == 1: 
                    ClusterBomb(
                        self.shape.right, self.shape.centerY, (3.5+YWing.boostLst[6]*0.1)*app.sizeMulti, 15+YWing.boostLst[5]*0.25, 
                        radius = 6*app.sizeMulti, clusterBombExplosionSize = (25+int(YWing.abilityBoostLst[3]*0.5))*app.sizeMulti, rA = 90, 
                        clusterBombExplosionDamage = 1+(YWing.boostLst[5]*0.05)/2, numBombs = 3+int(YWing.abilityBoostLst[8]/10), 
                        recursions = 0+int(YWing.abilityBoostLst[9]/10)
                    )
                else: 
                    ClusterBomb(
                        self.shape.right, self.shape.centerY, 3.5*app.sizeMulti, 15, radius = 6*app.sizeMulti, clusterBombExplosionSize = 25*app.sizeMulti, 
                        rA = 90, clusterBombExplosionDamage = 1, numBombs = 3, recursions = 0
                    )
                self.clusterCharges -= 1
            # updates ability bar, updates cooldowns and Charges
            if (
                (self.clusterCharges <= 0 and self.clusterEnabled) or (self.bombCharges <= 0 and self.bombEnabled) or 
                (self.empCharges <= 0 and self.empEnabled)
            ): 
                self.abilityBarBack.fill = 'darkkhaki'
            self.abilityBar.fill = 'yellow'
            self.abilityBar.x2 = self.shape.centerX+40*app.sizeMulti
            app.keys.remove(self.abilityKey)
        elif self.abilityCooldown > 0: 
            self.abilityCooldown -= 1
            self.abilityBar.fill = 'palegoldenrod'
            self.abilityBar.x2 = self.shape.centerX+(40-self.abilityCooldown*40/self.abilityCooldownMax)*app.sizeMulti
            self.abilityBar.lineWidth = 1.25*app.sizeMulti
        else: 
            self.abilityBarBack.fill = 'gold'
            self.abilityBar.fill = 'gold'
            self.abilityBar.lineWidth = 2.5*app.sizeMulti
            if self.bombCharges < self.bombChargesMax and self.bombEnabled: 
                self.bombCharges += 1
                self.abilityCooldown = self.abilityCooldownMax
            elif self.empCharges < self.empChargesMax and self.empEnabled: 
                self.empCharges += 1
                self.abilityCooldown = self.abilityCooldownMax
            elif self.clusterCharges < self.clusterChargesMax and self.clusterEnabled: 
                self.clusterCharges += 1
                self.abilityCooldown = self.abilityCooldownMax
class Falcon(Ship): 
    # ability: auto aim, regen hp
    # boosts
    boostLst = []
    for i in range(10): 
        boostLst.append(0)
    abilityBoostLst = []
    for i in range(2): 
        abilityBoostLst.append(0)
    abilityBoostNameLst = ["Ability Cooldown", "Ability Duration"]
    def __init__(self, cX, cY, upKey, downKey, rightKey, leftKey, shootKey, abilityKey, *, autoAimEnabled = False, healthRegenEnabled = False): 
        self.shape = Group(
            Polygon(338, 196, 270, 196, 265, 180, 338, 180, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98), start = 'left')), 
            Polygon(292, 196, 168, 220, 168, 196, fill = gradient(rgb(120, 125, 126), rgb(95, 98, 98), rgb(95, 98, 98), rgb(74, 75, 75), start = 'top')), 
            Polygon(153, 220, 153, 196, 29, 196, fill = gradient(rgb(120, 125, 126), rgb(95, 98, 98), rgb(95, 98, 98), rgb(74, 75, 75), start = 'top')), 
            Rect(153, 196, 15, 28, fill = rgb(95, 98, 98)), 
            Rect(29, 180, 51, 16, fill = 'lightBlue'), 
            Polygon(80, 180, 80, 196, 270, 196, 265, 180, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98))), 
            Line(80, 196, 196, 196), 
            Polygon(292, 180, 168, 164, 168, 180, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98), start = 'bottom')), 
            Polygon(153, 164, 153, 180, 29, 180, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98), start = 'bottom')), 
            Rect(153, 164, 15, 16, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98), start = 'bottom')), 
            Line(80, 180, 181, 180), 
            Circle(160, 192, 21, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(89, 93, 94), rgb(89, 93, 94))), 
            Polygon(
                154, 180, 164, 180, 172, 192, 164, 205, 154, 205, 147, 192, 
                fill = gradient(
                    rgb(89, 93, 94), rgb(89, 93, 94), rgb(74, 75, 75), rgb(74, 75, 75), rgb(74, 75, 75), rgb(74, 75, 75), rgb(74, 75, 75), 
                    rgb(74, 75, 75), 'darkRed', rgb(74, 75, 75), rgb(74, 75, 75), rgb(74, 75, 75), start = 'bottom'
                )
            ), 
            Polygon(168, 164, 202, 205, 240, 205, 240, 170, 206, 171, fill = gradient(rgb(120, 125, 126), rgb(89, 93, 94), rgb(89, 93, 94), start = 'bottom')), 
            Polygon(240, 170, 266, 177, 266, 192, 240, 205, fill = gradient(rgb(120, 125, 126), rgb(89, 93, 94), rgb(89, 93, 94), start = 'bottom')), 
            Line(240, 205, 266, 192, fill = rgb(89, 93, 94)), 
            Line(195, 196, 202, 205), 
            Line(168, 164, 195, 196), 
            Polygon(244, 172, 261, 180, 261, 182, 244, 180, fill = 'lightBlue'), 
            Polygon(153, 164, 168, 164, 164, 158, 157, 158, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98), start = 'bottom')), 
            Polygon(153, 224, 168, 224, 164, 230, 157, 230, fill = gradient(rgb(120, 125, 126), rgb(95, 98, 98), rgb(95, 98, 98), rgb(74, 75, 75), start = 'top')), 
            Line(164, 162, 173, 156), 
            Line(164, 227, 173, 229), 
            Oval(37, 188, 30, 20, fill = 'aqua', opacity = 32), 
            Line(206, 171, 206, 159, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98), start = 'bottom')), 
            Polygon(213, 145, 209, 152, 206, 159, 213, 168, 209, 158, fill = gradient(rgb(120, 125, 126), rgb(120, 125, 126), rgb(120, 125, 126), rgb(95, 98, 98), start = 'bottom'))
        )
        self.shape.height = 38/1.35*app.sizeMulti
        self.shape.width = 130/1.35*app.sizeMulti
        self.shape.centerX = cX
        self.shape.centerY = cY
        self.type = "F"
        self.autoAimEnabled = autoAimEnabled
        self.healthRegenEnabled = healthRegenEnabled
        self.moveWhileAbility = True
        self.keysLst = []
        # calls Ship constructor with different values depending on if the player chose multiplayer or not
        if app.numPlayers == 1: 
            self.abilityTimerMax = 6+Falcon.abilityBoostLst[1]
            self.abilityCooldownMax = 121-5*Falcon.abilityBoostLst[0]
            super().__init__(
                1.15*app.sizeMulti+(Falcon.boostLst[0]*0.25)*app.sizeMulti, 25-int(Falcon.boostLst[1]/2), 10+Falcon.boostLst[2], 
                8+Falcon.boostLst[3], 180-(Falcon.boostLst[4]*15), upKey, downKey, rightKey, leftKey, shootKey, abilityKey
            )
        else: 
            self.abilityTimerMax = 6
            self.abilityCooldownMax = 121
            super().__init__(1.15*app.sizeMulti, 25, 10, 8, 180, upKey, downKey, rightKey, leftKey, shootKey, abilityKey)
    # shoots Laser
    def shoot(self): 
        if app.numPlayers == 1: 
            Laser(
                self.shape.centerX-5*app.sizeMulti, self.shape.top-0.5*app.sizeMulti, 'red', (3.5+(Falcon.boostLst[6]*0.25))*app.sizeMulti, 1.5+(Falcon.boostLst[5]*0.25), 
                lW = 2*app.sizeMulti+(Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+(Falcon.boostLst[9]*0.5))*app.sizeMulti, piercing = 2+Falcon.boostLst[7]
            )
            Laser(
                self.shape.centerX-5*app.sizeMulti, self.shape.top+2.5*app.sizeMulti, 'red', (3.5+(Falcon.boostLst[6]*0.25))*app.sizeMulti, 1.5+(Falcon.boostLst[5]*0.25), 
                lW = 2*app.sizeMulti+(Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+(Falcon.boostLst[9]*0.5))*app.sizeMulti, piercing = 2+Falcon.boostLst[7]
            )
            Laser(
                self.shape.centerX-5*app.sizeMulti, self.shape.bottom-2.5*app.sizeMulti, 'red', (3.5+(Falcon.boostLst[6]*0.25))*app.sizeMulti, 1.5+(Falcon.boostLst[5]*0.25), 
                lW = 2*app.sizeMulti+(Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+(Falcon.boostLst[9]*0.5))*app.sizeMulti, piercing = 2+Falcon.boostLst[7]
            )
            Laser(
                self.shape.centerX-5*app.sizeMulti, self.shape.bottom+0.5*app.sizeMulti, 'red', (3.5+(Falcon.boostLst[6]*0.25))*app.sizeMulti, 1.5+(Falcon.boostLst[5]*0.25), 
                lW = 2*app.sizeMulti+(Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+(Falcon.boostLst[9]*0.5))*app.sizeMulti, piercing = 2+Falcon.boostLst[7]
            )
        else: 
            Laser(self.shape.centerX-5*app.sizeMulti, self.shape.top-0.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2)
            Laser(self.shape.centerX-5*app.sizeMulti, self.shape.top+2.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2)
            Laser(self.shape.centerX-5*app.sizeMulti, self.shape.bottom-2.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2)
            Laser(self.shape.centerX-5*app.sizeMulti, self.shape.bottom+0.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2)
    # defines what the Falcon's abilities do
    def ability(self): 
        if self.abilityKey in app.keys and self.abilityCooldown <= 0: 
            self.abilityTimer = self.abilityTimerMax
            self.abilityCooldown = self.abilityCooldownMax
            app.keys.remove(self.abilityKey)
        elif self.abilityTimer > 0: 
            # auto aim ability
            if self.autoAimEnabled: 
                if self.shotCooldown <= 0: 
                    self.shotCooldown = self.shotCooldownMax
                    self.abilityTimer -= 1
                    # finds where the hazard with the closest centerY on the top and bottom will be with some inaccuracy
                    topHazardDistance = 10000
                    topHazardX = 400*app.sizeMulti
                    topHazardY = self.shape.top
                    bottomHazardDistance = 10000
                    bottomHazardX = 400*app.sizeMulti
                    bottomHazardY = self.shape.bottom
                    for hazard in app.hazardLst: 
                        if hazard not in Laser.lst and hazard not in Explosion.lst and hazard.shape.left <= 400*app.sizeMulti: 
                            if hazard.shape.centerY < self.shape.centerY: 
                                newDistance = distance(0, self.shape.centerY, 0, hazard.shape.centerY)
                                if newDistance < topHazardDistance: 
                                    topHazardDistance = newDistance
                                    topHazardX = hazard.shape.centerX
                                    if hazard not in EnemyShip.lst: 
                                        if app.numPlayers == 1: 
                                            topHazardX = hazard.shape.centerX-hazard.speed*(newDistance/((3.5+Falcon.boostLst[6]*0.25)*app.sizeMulti)*app.sizeMulti)
                                        else: 
                                            topHazardX = hazard.shape.centerX-hazard.speed*(newDistance/(3.5*app.sizeMulti)*app.sizeMulti)
                                    topHazardY = hazard.shape.centerY
                            else: 
                                newDistance = distance(0, self.shape.centerY, 0, hazard.shape.centerY)
                                if newDistance < bottomHazardDistance: 
                                    bottomHazardDistance = newDistance
                                    bottomHazardX = hazard.shape.centerX
                                    if hazard not in EnemyShip.lst: 
                                        if app.numPlayers == 1: 
                                            bottomHazardX = hazard.shape.centerX-hazard.speed*(newDistance/((3.5+Falcon.boostLst[6]*0.25)*app.sizeMulti)*app.sizeMulti)
                                        else: 
                                            bottomHazardX = hazard.shape.centerX-hazard.speed*(newDistance/(3.5*app.sizeMulti)*app.sizeMulti)
                                    bottomHazardY = hazard.shape.centerY
                    # shoots Laser at nearest hazard
                    if app.numPlayers == 1: 
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top-0.5*app.sizeMulti, 'red', (3.5+Falcon.boostLst[6]*0.25)*app.sizeMulti, 
                            1.5+(Falcon.boostLst[5]*0.25), lW = (2+Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+Falcon.boostLst[9]*0.5)*app.sizeMulti, 
                            piercing = 2+Falcon.boostLst[7], rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top-0.5*app.sizeMulti, topHazardX, topHazardY-0.5*app.sizeMulti)
                        )
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top+2.5*app.sizeMulti, 'red', (3.5+Falcon.boostLst[6]*0.25)*app.sizeMulti, 
                            1.5+(Falcon.boostLst[5]*0.25), lW = (2+Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+Falcon.boostLst[9]*0.5)*app.sizeMulti, 
                            piercing = 2+Falcon.boostLst[7], rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top+2.5*app.sizeMulti, topHazardX, topHazardY+2.5*app.sizeMulti)
                        )
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top-2.5*app.sizeMulti, 'red', (3.5+Falcon.boostLst[6]*0.25)*app.sizeMulti, 
                            1.5+(Falcon.boostLst[5]*0.25), lW = (2+Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+Falcon.boostLst[9]*0.5)*app.sizeMulti, 
                            piercing = 2+Falcon.boostLst[7], rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top-2.5*app.sizeMulti, topHazardX, topHazardY-2.5*app.sizeMulti)
                        )
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top+0.5*app.sizeMulti, 'red', (3.5+Falcon.boostLst[6]*0.25)*app.sizeMulti, 
                            1.5+(Falcon.boostLst[5]*0.25), lW = (2+Falcon.boostLst[8]*0.25)*app.sizeMulti, length = (5+Falcon.boostLst[9]*0.5)*app.sizeMulti, 
                            piercing = 2+Falcon.boostLst[7], rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top+0.5*app.sizeMulti, topHazardX, topHazardY+0.5*app.sizeMulti)
                        )
                    else: 
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top-0.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 
                            1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2, 
                            rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top-0.5*app.sizeMulti, topHazardX, topHazardY-0.5*app.sizeMulti)
                        )
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top+2.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 
                            1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2, 
                            rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top+2.5*app.sizeMulti, topHazardX, topHazardY+2.5*app.sizeMulti)
                        )
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top-2.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 
                            1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2, 
                            rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top-2.5*app.sizeMulti, topHazardX, topHazardY-2.5*app.sizeMulti)
                        )
                        Laser(
                            self.shape.centerX-5*app.sizeMulti, self.shape.top+0.5*app.sizeMulti, 'red', 3.5*app.sizeMulti, 
                            1.5, lW = 2*app.sizeMulti, length = 5*app.sizeMulti, piercing = 2, 
                            rA = angleTo(self.shape.centerX-5*app.sizeMulti, self.shape.top+0.5*app.sizeMulti, topHazardX, topHazardY+0.5*app.sizeMulti)
                        )
                else: 
                    self.shotCooldown -= 1
            # updates ability bar and timers
            self.abilityBar.fill = 'yellow'
            self.abilityBar.x2 = self.shape.centerX+(self.abilityTimer*40/self.abilityTimerMax)*app.sizeMulti
        elif self.abilityCooldown > 0: 
            self.abilityCooldown -= 1
            self.abilityBar.fill = 'palegoldenrod'
            self.abilityBar.x2 = self.shape.centerX+(40-self.abilityCooldown*40/self.abilityCooldownMax)*app.sizeMulti
            self.abilityBar.lineWidth = 1.25
        else: 
            self.abilityBar.fill = 'gold'
            self.abilityBar.lineWidth = 2.5
class SupportShip: # auto ship
    # boosts
    lst = []
    boostLst = []
    for i in range(10): 
        boostLst.append(Rect(-1, -1, 1, 1))
        boostLst[i] = 0
    def __init__(self, cY, *, duration = 300): 
        self.shape = Group(
            Polygon(
                300, 198, 263, 184, 211, 176, 175, 160, 137, 146, 97, 148, 78, 164, 34, 172, 38, 204, 299, 204, 
                fill = gradient('grey', 'firebrick', 'grey', 'firebrick', 'grey', 'grey', 'grey', 'dimGrey', 'dimGrey', start = 'right')
            ), 
            Polygon(263, 183, 123, 172, 123, 147, 137, 146, 175, 154, 211, 176, fill = gradient('grey', 'black', 'grey', 'grey', 'grey', start = 'left')), 
            Polygon(
                76, 164, 26, 165, 24, 170, 26, 181, 74, 181, 75, 175, 139, 175, 139, 164, 
                fill = gradient('dimGrey', 'dimGrey', 'dimGrey', 'black', start = 'right'), 
                border = gradient('grey', 'dimGrey', start = 'left')
            ), 
            Polygon(
                76, 190, 26, 191, 24, 96, 26, 207, 74, 207, 75, 201, 139, 201, 139, 190, 
                fill = gradient('dimGrey', 'dimGrey', 'dimGrey', 'black', start = 'right'), 
                border = gradient('grey', 'dimGrey', start = 'left')
            ), 
            Line(65, 114, 130, 114, fill = 'dimGrey', lineWidth = 8), 
            Line(130, 114, 155, 114, lineWidth = 5, fill = 'dimGrey'), 
            Line(155, 114, 193, 114, lineWidth = 3, fill = 'dimGrey'), 
            Line(65, 251, 130, 251, fill = 'dimGrey', lineWidth = 8), 
            Line(130, 251, 155, 251, lineWidth = 5, fill = 'dimGrey'), 
            Line(155, 251, 193, 251, lineWidth = 3, fill = 'dimGrey'), 
            Polygon(93, 255, 116, 255, 133, 190, 72, 190, fill = gradient('gainsboro', 'dimGrey', start = 'bottom')), 
            Polygon(72, 175, 93, 110, 116, 110, 133, 175, fill = gradient('gainsboro', 'dimGrey', start = 'top')), 
            Polygon(72, 175, 72, 190, 133, 190, 133, 175, fill = gradient('dimGrey', 'black', 'dimGrey', start = 'top')), 
            Polygon(263, 184, 265, 189, 267, 194, 265, 200, 263, 204, 299, 204, 300, 198, fill = 'white')
        )
        self.shape.width = 70*0.8*app.sizeMulti
        self.shape.height = 40*0.8*app.sizeMulti
        self.shape.centerX = 45*app.sizeMulti
        self.shape.centerY = cY
        self.shotCooldown = 0
        if app.numPlayers == 1: 
            self.speed = 1.5*app.sizeMulti+SupportShip.boostLst[0]*app.sizeMulti
            self.shotCooldownMax = 8-int(SupportShip.boostLst[1])
            self.hp = 1+int(SupportShip.boostLst[2])
            self.shields = 1+int(SupportShip.boostLst[3])
            self.shieldCooldown = 150-int(SupportShip.boostLst[4])*15
            self.damage = 1+int(SupportShip.boostLst[5])
            self.piercing = 2+int(SupportShip.boostLst[7])
            self.shotLength = 6.5*app.sizeMulti+int(SupportShip.boostLst[9])*0.5*app.sizeMulti
            self.shotWidth = 3.5*app.sizeMulti+int(SupportShip.boostLst[8])*0.25*app.sizeMulti
            self.shotspeed = 6*app.sizeMulti+int(SupportShip.boostLst[6])*0.25*app.sizeMulti
        else: 
            self.speed = 1.5*app.sizeMulti
            self.shotCooldownMax = 8
            self.hp = 1
            self.shields = 1
            self.shieldCooldown = 150
        self.hpMax = self.hp
        self.shieldsMax = self.shields
        self.shieldCooldownMax = self.shieldCooldown
        self.type = "support"
        self.abilityCooldown = 0
        self.abilityTimer = 0
        self.duration = duration
        self.durationMax = duration
        self.stunned = False
        self.invTime = 25
        # information (hp, shield, shtCldwn, abltyCldwn) bars (lets the player know roughly what these values are at)
        self.healthBarBack = Line(
            self.shape.centerX-35*app.sizeMulti, self.shape.bottom+1.25*app.sizeMulti, self.shape.centerX+35*app.sizeMulti, 
            self.shape.bottom+1.25*app.sizeMulti, fill = 'seagreen', lineWidth = 2.5*app.sizeMulti
        )
        self.shieldBarBack = Line(
            self.shape.centerX-35*app.sizeMulti, self.shape.bottom+5*app.sizeMulti, self.shape.centerX+35*app.sizeMulti, 
            self.shape.bottom+5*app.sizeMulti, fill = 'cadetblue', lineWidth = 2.5*app.sizeMulti
        )
        self.shotCooldownBarBack = Line(
            self.shape.centerX-35*app.sizeMulti, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX, 
            self.shape.bottom+8.75*app.sizeMulti, fill =  'firebrick', lineWidth = 2.5*app.sizeMulti
        )
        self.abilityBarBack = Line(
            self.shape.centerX, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX+35*app.sizeMulti, 
            self.shape.bottom+8.75*app.sizeMulti, fill = 'darkkhaki', lineWidth = 2.5*app.sizeMulti
        )
        self.hpBar = Line(
            self.shape.centerX-35*app.sizeMulti, self.shape.bottom+1.25*app.sizeMulti, self.shape.centerX+35*app.sizeMulti, 
            self.shape.bottom+1.25*app.sizeMulti, fill = 'limegreen', lineWidth = 2.5*app.sizeMulti
        )
        self.shieldBar = Line(
            self.shape.centerX-35*app.sizeMulti, self.shape.bottom+5*app.sizeMulti, self.shape.centerX+35*app.sizeMulti, 
            self.shape.bottom+5*app.sizeMulti, fill = 'cyan', lineWidth = 2.5*app.sizeMulti)
        self.shieldCooldownBar = Line(
            self.shape.centerX-35*app.sizeMulti, self.shape.bottom+5*app.sizeMulti, self.shape.centerX+35*app.sizeMulti, 
            self.shape.bottom+5*app.sizeMulti, fill = 'lightcyan', lineWidth = 1.25*app.sizeMulti
        )
        self.shotCooldownBar = Line(
            self.shape.centerX-35*app.sizeMulti, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX, 
            self.shape.bottom+8.75*app.sizeMulti, fill = 'red', lineWidth = 2.5*app.sizeMulti
        )
        self.abilityBar = Line(
            self.shape.centerX, self.shape.bottom+8.75*app.sizeMulti, self.shape.centerX+35*app.sizeMulti, 
            self.shape.bottom+8.75*app.sizeMulti, fill = 'yellow', lineWidth = 2.5*app.sizeMulti
        )
        self.barGroup = Group(
            self.healthBarBack, self.shieldBarBack, self.shotCooldownBarBack, self.abilityBarBack, 
            self.hpBar, self.shieldBar, self.shieldCooldownBar, self.shotCooldownBar, self.abilityBar
        )
        Ship.lst.append(self)
        SupportShip.lst.append(self)
    def onStep(self): 
        if self.hp > 0: 
            self.invTime -= 1
            if not self.stunned: 
                # updates hp
                if self.shields < 0: 
                    self.hp += self.shields
                    self.shields = 0
                # regens shields
                if self.shields < self.shieldsMax: 
                    if self.shieldCooldown <= 0: 
                        self.shieldCooldown = self.shieldCooldownMax
                        self.shields += 1
                    else: 
                        self.shieldCooldown -= 1
                # shoots Laser
                if self.shotCooldown > 0: 
                    self.shotCooldown -= 1
                    self.shotCooldownBar.fill = 'crimson'
                    self.shotCooldownBar.lineWidth = 1.25*app.sizeMulti
                else: 
                    self.shoot()
                    self.shotCooldown = self.shotCooldownMax
                # hazard detection, goes after hazard with the closest centerY, if the hazard is too close, moves away
                hazardDistance = 1000000000
                hazardY = 200*app.sizeMulti
                hazardX = 200*app.sizeMulti
                hazardClose = False
                for hazard in app.hazardLst: 
                    if hazard.shape.visible and 0 <= hazard.shape.left <= 400: 
                        if distance(self.shape.right, self.shape.centerY, hazard.shape.left, hazard.shape.centerY) < hazardDistance: 
                            hazardDistance = distance(self.shape.right, self.shape.centerY, hazard.shape.left, hazard.shape.centerY)
                            hazardY = hazard.shape.centerY
                            hazardX = hazard.shape.left
                            if (hazardX < 95*app.sizeMulti and distance(0, self.shape.centerY, 0, hazard.shape.centerY) < hazard.shape.height/2+10*app.sizeMulti+self.speed+self.shape.height/2): 
                                hazardClose = True
                            else: 
                                hazardClose = False
                hazardDistance = 100*app.sizeMulti
                if len(EnemyShip.lst) != 0 and not hazardClose: 
                    for enemy in EnemyShip.lst: 
                        dist = distance(0, self.shape.centerY, 0, enemy.shape.centerY)
                        if dist <= hazardDistance: 
                            hazardY = enemy.shape.centerY
                            hazardX = enemy.shape.left
                            hazardDistance = dist
                # moves SupportShip
                if hazardY<self.shape.centerY: 
                    self.direction = -1
                elif hazardY > self.shape.centerY: 
                    self.direction = 1
                else: 
                    self.direction = 0
                if hazardClose: 
                    self.shape.centerY -= self.speed*self.direction
                else: 
                    self.shape.centerY += self.speed*self.direction
                if self.shape.top < 0: 
                    self.shape.top = 0
                elif self.shape.bottom > 400*app.sizeMulti: 
                    self.shape.bottom = 400*app.sizeMulti
            # updates information bars
            self.barGroup.centerX = self.shape.centerX
            self.barGroup.centerY = self.shape.bottom+7.5*app.sizeMulti
            self.hpBar.x2 = self.shape.centerX+(-35+self.hp*70/self.hpMax)*app.sizeMulti
            self.shieldBar.x2 = self.shape.centerX+(-35+self.shields*70/self.shieldsMax)*app.sizeMulti
            if self.shieldCooldownMax > 0: 
                self.shieldCooldownBar.x2 = self.shape.centerX+(35-self.shieldCooldown*70/self.shieldCooldownMax)*app.sizeMulti
            if self.shotCooldownMax > 0: 
                self.shotCooldownBar.x2 = self.shape.centerX+(-self.shotCooldown*35/self.shotCooldownMax)*app.sizeMulti
            if self.duration > 0: 
                self.duration -= 1
                self.abilityBar.x2 = self.shape.centerX+(self.duration*35/self.durationMax)*app.sizeMulti
            else: 
                self.hp = 0
                self.shields = 0
            self.shape.toFront()
            self.barGroup.toFront()
        else: 
            # removes SupportShip
            self.barGroup.visible = False
            removeObject(self)
    # shoots Laser
    def shoot(self): 
        if app.numPlayers == 1: 
            Laser(self.shape.centerX, self.shape.top+5*app.sizeMulti, 'red', self.shotspeed, self.damage, lW = self.shotWidth, length = self.shotLength, piercing = self.piercing)
            Laser(self.shape.centerX, self.shape.bottom-2*app.sizeMulti, 'red', self.shotspeed, self.damage, lW = self.shotWidth, length = self.shotLength, piercing = self.piercing)
        else: 
            Laser(self.shape.centerX, self.shape.top+5*app.sizeMulti, 'red', 6*app.sizeMulti, 1.5, lW = 3.5*app.sizeMulti, length = 6.5*app.sizeMulti, piercing = 2)
            Laser(self.shape.centerX, self.shape.bottom-2*app.sizeMulti, 'red', 6*app.sizeMulti, 1.5, lW = 3.5*app.sizeMulti, length = 6.5*app.sizeMulti, piercing = 2)
# how many upgrades of each type the player has that haven't been used
app.boostLst = []
for i in range(10): 
    app.boostLst.append(Rect(-1, -1, 1, 1))
    app.boostLst[i] = 0
app.lst = ["Speed", "Shot Cooldown", "Health", "Shield Strength", "Shield Cooldown", "Damage", "Shot Speed", "Shot Piercing", "Shot Width", "Shot Length"]
app.abilityBoostLstX = []
for i in range(5): 
    app.abilityBoostLstX.append(Rect(-1, -1, 1, 1))
    app.abilityBoostLstX[i] = 0
app.abilityBoostLstY = []
for i in range(10): 
    app.abilityBoostLstY.append(Rect(-1, -1, 1, 1))
    app.abilityBoostLstY[i] = 0
app.abilityBoostLstF = []
for i in range(2): 
    app.abilityBoostLstF.append(Rect(-1, -1, 1, 1))
    app.abilityBoostLstF[i] = 0
class Upgrade: 
    lst = []
    def __init__(self, cX, cY, i, *, b = None): 
        self.shape = Circle(cX+randrange(-10, 11)*app.sizeMulti, cY+randrange(-10, 11)*app.sizeMulti, 7.5*app.sizeMulti, fill = 'gold', border = b)
        self.index = i
        Upgrade.lst.append(self)
    # moves Upgrade, calls obtain function
    def move(self): 
        if self.shape.right > 0: 
            self.shape.centerX -= 5*app.sizeMulti
            for ship in Ship.lst: 
                if self.shape.hitsShape(ship.shape): 
                    self.obtain()
                    removeObject(self)
        else: 
            # removes Upgrade
            removeObject(self)
class BoostUpgrade(Upgrade): # Generic boosts
    def __init__(self, cX, cY, i): 
        super().__init__(cX, cY, i)
    def obtain(self): 
        app.boostLst[self.index] += 1
class AbilityUpgradeX(Upgrade): # XWing ability upgrades
    def __init__(self, cX, cY, i): 
        super().__init__(cX, cY, i, b = 'red')
    def obtain(self): 
        app.abilityBoostLstX[self.index] += 1
class AbilityUpgradeY(Upgrade): # YWing ability upgrades
    def __init__(self, cX, cY, i ): 
        super().__init__(cX, cY, i, b = 'green')
    def obtain(self): 
        app.abilityBoostLstY[self.index] += 1
class AbilityUpgradeF(Upgrade): # Falcon ability upgrades
    def __init__(self, cX, cY, i): 
        super().__init__(cX, cY, i, b =  'gray')
    def obtain(self): 
        app.abilityBoostLstF[self.index] += 1
class Level: 
    levelLst = []
    def __init__(
        self, *, tFAmount = 0, asteroidAmount = 0, tBAmount = 0, sDAmount = 0, tFSpawnRateMod = 1, tBSpawnRateMod = 1, 
        asteroidSpawnRateMod = 1, sDSpawnRateMod = 1, asteroidCapMod = 0, tFCapMod = 0, tBCapMod = 0, sDCapMod = 0
    ): 
        self.tFAmount = tFAmount
        self.tFDestroyed = 0
        self.asteroidAmount = asteroidAmount
        self.asteroidsDestroyed = 0
        self.tBAmount = tBAmount
        self.tBDestroyed = 0
        self.sDAmount = sDAmount
        self.sDDestroyed = 0
        self.asteroidSpawnRateMod = asteroidSpawnRateMod
        self.tFSpawnRateMod = tFSpawnRateMod
        self.tBSpawnRateMod = tBSpawnRateMod
        self.sDSpawnRateMod = sDSpawnRateMod
        self.asteroidCapMod = asteroidCapMod
        self.tFCapMod = tFCapMod
        self.tBCapMod = tBCapMod
        self.sDCapMod = sDCapMod
        Level.levelLst.append(self)
    # checks if the conditions to win the Level have been met
    def check(self): 
        app.asteroidRate = int(15*self.asteroidSpawnRateMod)
        app.asteroidCap = 25+self.asteroidCapMod
        app.tFCap = 15+self.tFCapMod
        app.tBCap = 10+self.tBCapMod
        app.sDCap = 5+self.sDCapMod
        if (
            self.asteroidsDestroyed >= self.asteroidAmount and self.tFDestroyed >= self.tFAmount and 
            self.tBDestroyed >= self.tBAmount and self.sDDestroyed >= self.sDAmount and len(Upgrade.lst) == 0
        ): 
            gameEnd()
            if app.level == app.highestLevel: 
                app.highestLevel += 1
    # resets the Level
    def reset(self): 
        self.tFDestroyed = 0
        self.asteroidsDestroyed = 0
        self.tBDestroyed = 0
        self.sDDestroyed = 0
# function that is called when the level is over or all player ships have been Dstryd
def gameEnd(): 
    if app.numPlayers == 2 or (app.numPlayers == 1 and app.shipDestroyed): 
        loseScore.value = "Your Score Was: "+str(app.score)
    if app.numPlayers == 2: 
        app.screen = "RetryLoseMultiplayer"
    elif app.numPlayers == 1 and app.shipDestroyed: 
        app.screen = "RetryLoseSingleplayer"
    else: 
        app.screen = "ContinueWin"
    while len(Asteroid.lst) > 0: 
        for a in Asteroid.lst: 
            removeObject(a)
    for s in Ship.lst: 
        s.barGroup.visible = False
        removeObject(s)
    for l in Level.levelLst: 
        l.reset()
    clearscreen()
    app.play = False
# removes all Projectiles, EnemyShips, EMPs, Explosions, and Upgrades and resets all Asteroids
def removeObject(o): 
    o.shape.visible = False
    if o in app.hazardLst: 
        app.hazardLst.remove(o)
    if o in EnemyShip.lst: 
        EnemyShip.lst.remove(o)
    if o in Projectile.lst: 
        Projectile.lst.remove(o)
    if o in Explosion.lst: 
        Explosion.lst.remove(o)
    if o in EMP.lst: 
        EMP.lst.remove(o)
    if o in Upgrade.lst: 
        Upgrade.lst.remove(o)
    if o in Ship.lst: 
        Ship.lst.remove(o)
    if o in TieFighter.lst: 
        TieFighter.lst.remove(o)
    if o in TieBomber.lst: 
        TieBomber.lst.remove(o)
    if o in StarDestroyer.lst: 
        StarDestroyer.lst.remove(o)
    if o in Asteroid.lst: 
        Asteroid.lst.remove(o)
    if o in Laser.lst: 
        Laser.lst.remove(o)
    if o in Bomb.lst: 
        Bomb.lst.remove(o)
    if o in IonBlast.lst: 
        IonBlast.lst.remove(o)
    if o in SupportShip.lst: 
        SupportShip.lst.remove(o)
def clearscreen(): 
    for a in Asteroid.lst: 
        a.reset()
    while len(EnemyShip.lst) > 0: 
        for e in EnemyShip.lst: 
            removeObject(e)
    while len(Projectile.lst) > 0: 
        for p in Projectile.lst: 
            removeObject(p)
    while len(Explosion.lst) > 0: 
        for e in Explosion.lst: 
            removeObject(e)
    while len(EMP.lst) > 0: 
        for e in EMP.lst: 
            removeObject(e)
    while len(Upgrade.lst) > 0: 
        for u in Upgrade.lst: 
            removeObject(u)
# spawns a random Upgrade
def upgradeSpawn(cX, cY): 
    u = randrange(0, 11)
    if u < 10: 
        BoostUpgrade(cX, cY, u)
    elif u == 10: 
        au = randrange(0, 3)
        if au == 0: 
            aux = randrange(0, len(app.abilityBoostLstX))
            AbilityUpgradeX(cX, cY, aux)
        elif au == 1: 
            auy = randrange(0, len(app.abilityBoostLstY))
            AbilityUpgradeY(cX, cY, auy)
        elif au == 2: 
            auf = randrange(0, len(app.abilityBoostLstF))
            AbilityUpgradeF(cX, cY, auf)
# retry button
retry = Group(
    Rect(150, 150, 100, 100, border = 'white'), Arc(200, 200, 75, 75, 90, 270, border = 'white', borderWidth = 10), 
    Circle(200, 200, 28), RegularPolygon(203, 169, 15, 3, fill = 'white', rotateAngle = 90)
)
retry.width = 75*app.sizeMulti
retry.height = 75*app.sizeMulti
retry.centerX = 200*app.sizeMulti
retry.centerY = 200*app.sizeMulti
winContinue = Group(Rect(150, 150, 100, 100, border = 'white'), RegularPolygon(200, 200, 35, 3, rotateAngle = 90, border = 'white'))
winContinue.width = 75*app.sizeMulti
winContinue.height = 75*app.sizeMulti
winContinue.centerX = 200*app.sizeMulti
winContinue.centerY = 200*app.sizeMulti
# leaderboard (multiplayer)
backgroundAndTitle = Group(
    Rect(25*app.sizeMulti, 25*app.sizeMulti, 350*app.sizeMulti, 355*app.sizeMulti, fill = 'tan', borderWidth = 5*app.sizeMulti, border = 'black'), 
    Label('Leaderboard', 200*app.sizeMulti, 50*app.sizeMulti, font = 'orbitron', size = 35*app.sizeMulti), 
    Line(30*app.sizeMulti, 69*app.sizeMulti, 370*app.sizeMulti, 69*app.sizeMulti)
)
rounds = Group()
for y in range(8): 
    rounds.add(Label('Round '+str(y+1)+ ' : ', 78*app.sizeMulti, (y*35+119)*app.sizeMulti, size = 18*app.sizeMulti, font = 'orbitron'))
for round in rounds: 
    round.left = 32
stats = Group(
    Label('ROUND #', 78*app.sizeMulti, 84*app.sizeMulti, size = 18*app.sizeMulti, font = 'orbitron'), 
    Label('Score', 180*app.sizeMulti, 84*app.sizeMulti, size = 18*app.sizeMulti, font = 'orbitron'), 
    Label('Ship', 260*app.sizeMulti, 84*app.sizeMulti, size = 18*app.sizeMulti, font = 'orbitron'), 
    Label('Name', 325*app.sizeMulti, 84*app.sizeMulti, size = 18*app.sizeMulti, font = 'orbitron'), 
    Line(30*app.sizeMulti, 96*app.sizeMulti, 370*app.sizeMulti, 96*app.sizeMulti)
)
for y in range(7): 
    stats.add(Line(30*app.sizeMulti, (y*35+135)*app.sizeMulti, 370*app.sizeMulti, (y*35+135)*app.sizeMulti))
stats.add(
    Line(135*app.sizeMulti, 69*app.sizeMulti, 135*app.sizeMulti, 375*app.sizeMulti), 
    Line(225*app.sizeMulti, 69*app.sizeMulti, 225*app.sizeMulti, 375*app.sizeMulti), 
    Line(290*app.sizeMulti, 69*app.sizeMulti, 290*app.sizeMulti, 375*app.sizeMulti))
app.round = 1
scoreLst = []
scoreWinner = Group()
shipLabel = Group()
nameLabels = Group()
# screens
continueNd = Group(
    Rect(315*app.sizeMulti, 365*app.sizeMulti, 80*app.sizeMulti, 30*app.sizeMulti, border = 'white'), 
    Label('Continue', 355*app.sizeMulti, 380*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white')
)
stars = Group()
for i in range(100): 
    stars.add(Circle(randrange(0, 400)*app.sizeMulti, randrange(0, 400)*app.sizeMulti, 1*app.sizeMulti, fill = 'white'))
#['It`s Not A Chicken Sacrifice, ', 'It`s a Cockpit'], 
# Menu and buttons
naming = [
    ['Oops, I Bumped', 'Into An Asteroid'], ['Gimme Some', 'Space'], ['Aw Ship, ', 'I Can`t Breath'], ['Stop Star-ing', 'At Me'], 
    ['It`s A', 'Flying Pan'], ['It`s A Bird, It`s A Plane, ', 'No, It`s a Trap!'], ['Space', 'Your Fears'], ['Hey Sir, ', 'It`s a Laser'], 
    ['Make Sure to Travel Light, ', 'We Prioritize Speed'], ['Make Sure to Get', 'Your Booster Shot'], ['Don`t be Hyper, ', 'It`s just Space'], 
    ['Punch It!', 'Wait, Not Literally'], ['Face the', 'Space'], ['Fire!', 'Get The Water'], 
    ['Shoot!', 'Score!'], ['X-wing, X-wing', 'read all about it!'], ['It`s not a wrestling draw, ', 'It`s a Tie Fighter'], ['Just Wing', 'It!'], 
    ['It`s a Bow Tie', 'Fighter'], ['Dont Shove Me', 'In Your Air Lock-er'], ['There`s a Hole', 'In The Hull'], ['Dont Plan-it', 'Go To A Planet'], 
    ['Vroom', 'Vroom'], ['You Can Breath', 'In Space'], ['Ewok', 'And Roll'], ['The Senator Is On', 'The Venator'], ['*Angry Droid', 'Noises*'], 
    ['OHHH... You Wanted', 'Your Arms!'], ['Chugga Chugga Chugga', 'Chew-bacca'], ['We Lost Power Captain!', 'That`s Just Our Ion Missile'], 
    ['This Game Is', 'Da Bomb'], ['Kick Em` In', 'The Shins']
]
subtitle = randrange(0, len(naming))
logo = Group(
    Label('Star Wars', 200*app.sizeMulti, 50*app.sizeMulti, size = 50*app.sizeMulti, fill = 'white'), 
    Label(naming[subtitle][0], 200*app.sizeMulti, 100*app.sizeMulti, size = 20*app.sizeMulti, fill = 'white'), 
    Label(naming[subtitle][1], 200*app.sizeMulti, 130*app.sizeMulti, size = 20*app.sizeMulti, fill = 'white')
)
solo = Group(
    Rect(100*app.sizeMulti, 150*app.sizeMulti, 200*app.sizeMulti, 50*app.sizeMulti, fill = 'black', border = 'red'), 
    Label('Solo Fighter', 200*app.sizeMulti, 175*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white')
)
multiplayer = Group(
    Rect(100*app.sizeMulti, 220*app.sizeMulti, 200*app.sizeMulti, 50*app.sizeMulti, fill = 'black', border = 'aqua'), 
    Label('Multiplayer', 200*app.sizeMulti, 245*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white')
)
upgradeButton = Group(
    Rect(100*app.sizeMulti, 290*app.sizeMulti, 200*app.sizeMulti, 50*app.sizeMulti, fill = 'black', border = 'gray'), 
    Label('Upgrade', 200*app.sizeMulti, 315*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white')
)
importButton = Group(
    Rect(115*app.sizeMulti, 360*app.sizeMulti, 70*app.sizeMulti, 30*app.sizeMulti, fill = 'black', border = 'gold'), 
    Label("Import", 150*app.sizeMulti, 375*app.sizeMulti, fill = 'white', size = 20*app.sizeMulti)
)
exportButton = Group(
    Rect(215*app.sizeMulti, 360*app.sizeMulti, 70*app.sizeMulti, 30*app.sizeMulti, fill = 'black', border = 'limegreen'), 
    Label("Export", 250*app.sizeMulti, 375*app.sizeMulti, fill = 'white', size = 20*app.sizeMulti)
)
buttonY = Circle(100*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'black', border = 'aqua')
labelY = Label('Y', 100*app.sizeMulti, 300*app.sizeMulti, size = 40*app.sizeMulti, fill = 'aqua', border = 'aqua')
choosingYWing = Group(buttonY, labelY)
buttonX = Circle(300*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
labelX = Label('X', 300*app.sizeMulti, 300*app.sizeMulti, size = 40*app.sizeMulti, fill = 'aqua', border = 'aqua')
choosingXWing = Group(buttonX, labelX)
buttonF = Circle(200*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
labelF = Label('F', 200*app.sizeMulti, 300*app.sizeMulti, size = 40*app.sizeMulti, fill = 'aqua', border = 'aqua')
choosingFalcon = Group(buttonF, labelF)
choosingGroup = Group(choosingYWing, choosingXWing, choosingFalcon)
shipChooseGroupDict = {"y": choosingYWing, "f": choosingFalcon, "x": choosingXWing}
shipChooseDict = {choosingYWing: "y", choosingFalcon: "f", choosingXWing: "x"}
bombLabel = Label('BOMB', 100*app.sizeMulti, 300*app.sizeMulti, size = 22*app.sizeMulti, fill = 'aqua', border = 'aqua')
bombButton = Circle(100*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'black', border = 'aqua')
empLabel = Label('EMP', 300*app.sizeMulti, 300*app.sizeMulti, size = 30*app.sizeMulti, fill = 'aqua', border = 'aqua')
empButton = Circle(300*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
clusterBombLabel = Label('C-BOMB', 200*app.sizeMulti, 300*app.sizeMulti, size = 18*app.sizeMulti, fill = 'aqua', border = 'aqua')
clusterBombButton = Circle(200*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
abilityChooseGroupY = Group(bombButton, bombLabel, empButton, empLabel, clusterBombButton, clusterBombLabel, visible = False)
autoAimLabel = Label('AUTO-AIM', 250*app.sizeMulti, 300*app.sizeMulti, size = 14*app.sizeMulti, fill = 'aqua', border = 'aqua')
autoAimButton = Circle(250*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
hpRegenLabel = Label('HP-REGEN', 150*app.sizeMulti, 300*app.sizeMulti, size = 13.5*app.sizeMulti, fill = 'aqua', border = 'aqua')
hpRegenButton = Circle(150*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
abilityChooseGroupF = Group(autoAimButton, autoAimLabel, hpRegenButton, hpRegenLabel, visible = False)
dashLabel = Label('DASH', 250*app.sizeMulti, 300*app.sizeMulti, size = 22*app.sizeMulti, fill = 'aqua', border = 'aqua')
dashButton = Circle(250*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
supportLabel = Label('SUPPORT', 150*app.sizeMulti, 300*app.sizeMulti, size = 14*app.sizeMulti, fill = 'aqua', border = 'aqua')
supportButton = Circle(150*app.sizeMulti, 300*app.sizeMulti, 40*app.sizeMulti, fill = 'Black', border = 'aqua')
abilityChooseGroupX = Group(dashLabel, dashButton, supportButton, supportLabel, visible = False)
abilityYChooseLabelLst = [bombLabel, empLabel, clusterBombLabel]
abilityYChooseButtonLst = [bombButton, empButton, clusterBombButton]
abilityXChooseLabelLst = [dashLabel, supportLabel]
abilityXChooseButtonLst = [dashButton, supportButton]
abilityFChooseLabelLst = [autoAimLabel, hpRegenLabel]
abilityFChooseButtonLst = [autoAimButton, hpRegenButton]
abilityChooseScreenDict = {"y": abilityChooseGroupY, "f": abilityChooseGroupF, "x": abilityChooseGroupX}
abilityChooseButtonDict = {"y": abilityYChooseButtonLst, "f": abilityFChooseButtonLst, "x": abilityXChooseButtonLst}
abilityChooseLabelDict = {"y": abilityYChooseLabelLst, "f": abilityFChooseLabelLst, "x": abilityXChooseLabelLst}
abilityChooseAbilityDict = {bombButton: "yb", empButton: "ye", clusterBombButton: "yc", autoAimButton: "fa", hpRegenButton: "fh", dashButton: "xd", supportButton: "xs"}
abilityDict = {"y": "N", "x": "N", "f": "N"}
abilityChooseShipLabelGroup = Group(
    Label("X-Wing", 50*app.sizeMulti, 300*app.sizeMulti, fill = 'white', size = 25*app.sizeMulti), 
    Label("Falcon", 50*app.sizeMulti, 100*app.sizeMulti, fill = 'white', size = 25*app.sizeMulti), 
    Label("Y-Wing", 50*app.sizeMulti, 200*app.sizeMulti, fill = 'white', size = 25*app.sizeMulti)
)
# level selection
levelScreenGroup = Group()
level = 1
for i in range(4): 
    for a in range(4): 
        levelScreenGroup.add(Group(Rect(25*app.sizeMulti+75*app.sizeMulti*a, 25*app.sizeMulti+75*app.sizeMulti*i, 50*app.sizeMulti, 50*app.sizeMulti, border = 'white'), Label(level, 50*app.sizeMulti+75*app.sizeMulti*a, 50*app.sizeMulti+75*app.sizeMulti*i, font = 'orbitron', fill = 'white', 
        size = 20*app.sizeMulti)))
        level += 1
for i in levelScreenGroup: 
    i.chosen = False
levelScreenGroup.centerX = 200*app.sizeMulti
levelScreenGroup.centerY = 200*app.sizeMulti
shipScreen = Label('Choose Your Ship', 200*app.sizeMulti, 20*app.sizeMulti, fill = 'white', size = 40*app.sizeMulti)
abilityScreen = Label('Choose Your Ability', 200*app.sizeMulti, 20*app.sizeMulti, fill = 'white', size = 40*app.sizeMulti)
# Asteroids
for i in range(5): 
    Asteroid()
# Control Screen
ywingControls = Group(
    Label('Y-Wing', 60*app.sizeMulti, 80*app.sizeMulti, size = 25*app.sizeMulti, fill = 'white'), 
    Label('Movement', 60*app.sizeMulti, 115*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('W', 60*app.sizeMulti, 150*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Label('A', 30*app.sizeMulti, 190*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Label('D', 90*app.sizeMulti, 190*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Label('S', 60*app.sizeMulti, 190*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Label('Shoot', 60*app.sizeMulti, 215*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Rect(45*app.sizeMulti, 235*app.sizeMulti, 30*app.sizeMulti, 30*app.sizeMulti, fill = None, border = 'white', borderWidth = 3*app.sizeMulti), 
    Label('Q', 60*app.sizeMulti, 250*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('E', 60*app.sizeMulti, 325*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('Ability', 60*app.sizeMulti, 290*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Rect(45*app.sizeMulti, 310*app.sizeMulti, 30*app.sizeMulti, 30*app.sizeMulti, fill = None, border = 'white', borderWidth = 3*app.sizeMulti)
)
xwingControls = Group(
    Label('X-Wing', 340*app.sizeMulti, 80*app.sizeMulti, size = 25*app.sizeMulti, fill = 'white'), 
    Label('Movement', 340*app.sizeMulti, 115*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Line(340*app.sizeMulti, 150*app.sizeMulti, 340*app.sizeMulti, 165*app.sizeMulti, fill = 'white'), 
    RegularPolygon(340*app.sizeMulti, 150*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white'), 
    Line(340*app.sizeMulti, 175*app.sizeMulti, 340*app.sizeMulti, 190*app.sizeMulti, fill = 'white'), 
    RegularPolygon(340*app.sizeMulti, 190*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white', rotateAngle = 180), 
    Line(310*app.sizeMulti, 170*app.sizeMulti, 325*app.sizeMulti, 170*app.sizeMulti, fill = 'white'), 
    RegularPolygon(310*app.sizeMulti, 170*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white', rotateAngle = 270), 
    Line(355*app.sizeMulti, 170*app.sizeMulti, 370*app.sizeMulti, 170*app.sizeMulti, fill = 'white'), 
    RegularPolygon(370*app.sizeMulti, 170*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white', rotateAngle = 90), 
    Label('Shoot', 340*app.sizeMulti, 215*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('Space', 340*app.sizeMulti, 250*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Rect(280*app.sizeMulti, 230*app.sizeMulti, 120*app.sizeMulti, 45*app.sizeMulti, fill = None, border = 'white', borderWidth = 3*app.sizeMulti), 
    Label('C', 340*app.sizeMulti, 325*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('Ability', 340*app.sizeMulti, 290*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Rect(325*app.sizeMulti, 310*app.sizeMulti, 30*app.sizeMulti, 30*app.sizeMulti, fill = None, border = 'white', borderWidth = 3*app.sizeMulti)
)
falconControls = Group(
    Label('Falcon', 200*app.sizeMulti, 80*app.sizeMulti, size = 25*app.sizeMulti, fill = 'white'), 
    Label('Movement', 200*app.sizeMulti, 115*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('I', 200*app.sizeMulti, 150*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Label('J', 170*app.sizeMulti, 190*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Label('L', 230*app.sizeMulti, 190*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'),
    Label('K', 200*app.sizeMulti, 190*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Label('Shoot', 200*app.sizeMulti, 215*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Rect(185*app.sizeMulti, 235*app.sizeMulti, 30*app.sizeMulti, 30*app.sizeMulti, fill = None, border = 'white', borderWidth = 3*app.sizeMulti), 
    Label('U', 200*app.sizeMulti, 250*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('O', 200*app.sizeMulti, 325*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('Ability', 200*app.sizeMulti, 290*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Rect(185*app.sizeMulti, 310*app.sizeMulti, 30*app.sizeMulti, 30*app.sizeMulti, fill = None, border = 'white', borderWidth = 3*app.sizeMulti)
)
soloControls = Group(
    Label('Controls', 200*app.sizeMulti, 80*app.sizeMulti, size = 25*app.sizeMulti, fill = 'white'), 
    Label('Movement', 200*app.sizeMulti, 115*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Line(200*app.sizeMulti, 150*app.sizeMulti, 200*app.sizeMulti, 165*app.sizeMulti, fill = 'white'), 
    RegularPolygon(200*app.sizeMulti, 150*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white'), 
    Line(200*app.sizeMulti, 175*app.sizeMulti, 200*app.sizeMulti, 190*app.sizeMulti, fill = 'white'), 
    RegularPolygon(200*app.sizeMulti, 190*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white', rotateAngle = 180), 
    Line(170*app.sizeMulti, 170*app.sizeMulti, 185*app.sizeMulti, 170*app.sizeMulti, fill = 'white'), 
    RegularPolygon(170*app.sizeMulti, 170*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white', rotateAngle = 270), 
    Line(215*app.sizeMulti, 170*app.sizeMulti, 230*app.sizeMulti, 170*app.sizeMulti, fill = 'white'), 
    RegularPolygon(230*app.sizeMulti, 170*app.sizeMulti, 6*app.sizeMulti, 3, fill = 'white', rotateAngle = 90), 
    Label('Shoot', 200*app.sizeMulti, 215*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('Space', 200*app.sizeMulti, 250*app.sizeMulti, size = 30*app.sizeMulti, fill = 'white'), 
    Rect(140*app.sizeMulti, 230*app.sizeMulti, 120*app.sizeMulti, 45*app.sizeMulti, fill = None, border = 'white', borderWidth = 3), 
    Label('Ability', 200*app.sizeMulti, 290*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Label('C', 200*app.sizeMulti, 325*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white'), 
    Rect(185*app.sizeMulti, 310*app.sizeMulti, 30*app.sizeMulti, 30*app.sizeMulti, fill = None, border = 'white', borderWidth = 3*app.sizeMulti)
)
continueControlScreen = Group(
    Rect(275*app.sizeMulti, 355*app.sizeMulti, 120*app.sizeMulti, 40*app.sizeMulti, fill = 'black', border = 'white'), 
    Label('Continue', 335*app.sizeMulti, 375*app.sizeMulti, size = 25*app.sizeMulti, fill = 'white')
)
# app properties
app.keys = []
app.numPlayers = 0
app.ship = "z"
app.play = False
app.asteroidRate = 15
app.asteroidCap = 25
# score and lose screen
app.score = 0
app.tFCooldown = randrange(150, 300)
app.tFCap = 15
app.tBCooldown = randrange(150, 300)
app.tBCap = 10
app.sDCooldown = randrange(150, 300)
app.sDCap = 5
app.shipDestroyed = False
app.lastShip = "X"
loseScore = Label("You Dodged "+str(app.score)+" Asteroids", 200*app.sizeMulti, 125*app.sizeMulti, size = 25*app.sizeMulti, fill = 'red', font = 'orbitron')
loseScreen = Group(Label('You Lose!', 200*app.sizeMulti, 75*app.sizeMulti, size = 50*app.sizeMulti, fill = 'red', font = 'orbitron'), loseScore)
scoreLabel = Label(app.score, 20*app.sizeMulti, 10*app.sizeMulti, fill = 'white', size = 15*app.sizeMulti)
leaderboardContinue = Group(
    Rect(315*app.sizeMulti, 365*app.sizeMulti, 80*app.sizeMulti, 30*app.sizeMulti, border = 'white'), 
    Label('Continue', 355*app.sizeMulti, 380*app.sizeMulti, size = 15*app.sizeMulti, fill = 'white')
)
# Levels
Level(tFAmount = 2)
Level(tFAmount = 5)
Level(tFAmount = 6, tBAmount = 1)
Level(tFAmount = 8, tBAmount = 3)
Level(tFAmount = 10, tBAmount = 5, sDAmount = 1)
Level(tFAmount = 13, tBAmount = 8, sDAmount = 3)
Level(tFAmount = 15, tBAmount = 10, sDAmount = 5)
Level(tFAmount = 20, tBAmount = 12, sDAmount = 6)
Level(tFAmount = 23, tBAmount = 15, sDAmount = 8)
Level(tFAmount = 27, tBAmount = 17, sDAmount = 9)
Level(tFAmount = 30, tBAmount = 20, sDAmount = 10)
Level(tFAmount = 33, tBAmount = 22, sDAmount = 11)
Level(tFAmount = 35, tBAmount = 25, sDAmount = 15)
Level(tFAmount = 37, tBAmount = 27, sDAmount = 17)
Level(tFAmount = 40, tBAmount = 30, sDAmount = 20)
Level(tFAmount = 10000000, tBAmount = 10000000, sDAmount = 10000000, tFSpawnRateMod = 0.5, tBSpawnRateMod = 0.5, asteroidSpawnRateMod = -10, 
sDSpawnRateMod = 0.5, asteroidCapMod = 25, tFCapMod = 35, tBCapMod = 40, sDCapMod = 45)
app.highestLevel = 0
app.screen = "Home"
app.screenLst = [
    "Home", "Level", "ChooseShip", "AbilityMultiplayer", "multiplayer", "AbilitySingleplayer", "soloControls", 
    "RetryLoseSingleplayer", "RetryLoseMultiplayer", "ContinueWin", "LeaderBoard", "Playing"
]
app.screenGroupDict = {
    "Home": [upgradeButton, solo, multiplayer, logo, importButton, exportButton], 
    "Level": [levelScreenGroup, continueControlScreen], 
    "ChooseShip": [shipScreen, continueControlScreen, choosingGroup], 
    "AbilitySingleplayer": [abilityScreen, continueControlScreen], 
    "AbilityMultiplayer": [abilityScreen, abilityChooseShipLabelGroup, continueControlScreen], 
    "multiplayer": [ywingControls, xwingControls, falconControls, continueControlScreen], 
    "soloControls": [soloControls, continueControlScreen], 
    "RetryLoseSingleplayer": [retry, loseScreen], 
    "RetryLoseMultiplayer": [loseScreen, continueNd], 
    "ContinueWin": [winContinue], 
    "LeaderBoard": [scoreWinner, shipLabel, nameLabels, rounds, stats, backgroundAndTitle, leaderboardContinue],
    "Playing": []
}
app.asteroidSizeMod = 0
app.enemyHPMod = 0
app.enemyCooldownMod = 0
app.enemyDMGMod = 0
app.stepsPerSecond = 45
def screenCheck(): 
    for s in app.screenLst: 
        for g in app.screenGroupDict[s]: 
            if g not in app.screenGroupDict[app.screen]: 
                g.visible = False
            else: 
                g.visible = True
def leaderboardScreen(name): 
    scoreLst.append(app.score)
    namesRow = app.round-1
    if app.round <= 8: 
        scoreWinner.add(Label(app.score, 180*app.sizeMulti, 80*app.sizeMulti+app.round*35*app.sizeMulti, size = 20*app.sizeMulti))
        shipLabel.add(Label(app.lastShip, 257*app.sizeMulti, 80*app.sizeMulti+app.round*35*app.sizeMulti, size = 20*app.sizeMulti))
        if name == '': 
            name = app.getTextInput()
        nameLabels.add(Label(str(name), 330*app.sizeMulti, namesRow*35*app.sizeMulti+115*app.sizeMulti, size = 20*app.sizeMulti))
    else: 
        nameLabels.clear()
        scoreWinner.clear()
        shipLabel.clear()
        app.round = 1
# game
def onStep(): 
    # Moving the stars
    for star in stars: 
        if star.right > 0: 
            star.centerX -= 5*app.sizeMulti
        else: 
            star.left = 405*app.sizeMulti
    if app.play: 
        scoreLabel.visible = True
        # ends the game if all player Ships are Dstryd
        if len(Ship.lst) == 0: 
            app.shipDestroyed = True
            gameEnd()
        # updates Ships
        for ship in Ship.lst: 
            ship.onStep()
        # updates score label
        scoreLabel.value = app.score
        scoreLabel.toFront()
        # moves Projectiles
        for p in Projectile.lst: 
            p.move()
        # Explosions/EMPs
        for e in EMP.lst: 
            e.stun()
        for e in Explosion.lst: 
            e.explode()
        # moves Asteroids
        for a in Asteroid.lst: 
            a.move()
        # moves Upgrades
        for u in Upgrade.lst: 
            u.move()
        if app.numPlayers == 2: 
            # checks what the last Ship that is still alive is
            if len(Ship.lst) != 0: 
                if Ship.lst[0].type == "Y": 
                    app.lastShip = "Y-Wing"
                elif Ship.lst[0].type == "X": 
                    app.lastShip = "X-Wing"
                elif Ship.lst[0].type == "F": 
                    app.lastShip = "Falcon"
        elif app.numPlayers == 1: 
            Level.levelLst[app.level].check()
        # EnemyShip spawning and moving
        if app.score > 30: 
            if app.tFCooldown <= 0: 
                if app.numPlayers == 1: 
                    app.tFCooldown = int(randrange(210, 600)*Level.levelLst[app.level].tFSpawnRateMod)-int(app.score/3)
                else: 
                    app.tFCooldown = randrange(210, 600)-int(app.score/2)
                if app.tFCooldown < 15: 
                    app.tFCooldown = 15
                if len(TieFighter.lst) < app.tFCap: 
                    TieFighter(randrange(20, 381)*app.sizeMulti)
            else: 
                app.tFCooldown -= 1
            if app.score > 60 and app.level > 1: 
                if app.tBCooldown <= 0: 
                    if app.numPlayers == 1: 
                        app.tBCooldown = int(randrange(450, 900)*Level.levelLst[app.level].tBSpawnRateMod)-int(app.score/3)
                    else: 
                        app.tBCooldown = randrange(450, 900)-int(app.score/3)
                    if app.tBCooldown < 15: 
                        app.tBCooldown = 15
                    if len(TieBomber.lst) < app.tBCap: 
                        TieBomber(randrange(20, 381)*app.sizeMulti)
                else: 
                    app.tBCooldown -= 1
                if app.score > 90 and app.level > 3: 
                    if app.sDCooldown <= 0: 
                        if app.numPlayers == 1: 
                            app.sDCooldown = int(randrange(510, 900)*Level.levelLst[app.level].sDSpawnRateMod)-int(app.score/3)
                        else: 
                            app.sDCooldown = randrange(510, 900)-int(app.score/3)
                        if app.sDCooldown < 15: 
                            app.sDCooldown = 15
                        if len(StarDestroyer.lst) < app.sDCap: 
                            StarDestroyer(randrange(25, 391)*app.sizeMulti)
                    else: 
                        app.sDCooldown -= 1
        for enemy in EnemyShip.lst: 
            enemy.move()
    else: 
        scoreLabel.visible = False
        screenCheck()
# starts the game
def start(): 
    app.play = True
    app.screen = "Playing"
    sLst = ["x", "y", "f"]
    for s in sLst: 
        abilityChooseScreenDict[s].visible = False
    screenCheck()
# resets values to original values
def reset(): 
    clearscreen()
    app.numPlayers = 0
    app.score = 0
    app.shipDestroyed = False
    app.ship = 'z'
    for i in choosingGroup: 
        changeBorderColor(i, 'aqua')
    app.tFCooldown = randrange(150, 300)
    app.tBCooldown = randrange(300, 450)
    app.sDCooldown = randrange(150, 300)
    for i in range(5): 
        Asteroid()
    app.screen = "Home"
def changeBorderColor(group, color): 
    for i in group: 
        i.border = color
def abilityButtonCheck(s, x, y): 
    gnum = 0
    for g in abilityChooseButtonDict[s]: 
        if g.hits(x, y) and g.visible: 
            abilityDict[s] = abilityChooseAbilityDict[g]
            changeBorderColor(abilityChooseButtonDict[s], 'aqua')
            abilityChooseButtonDict[s][gnum].border = 'red'
            changeBorderColor(abilityChooseLabelDict[s], 'aqua')
            abilityChooseLabelDict[s][gnum].border = 'red'
        gnum += 1
# buttons
def onMousePress(x, y): 
    # start screens
    if app.screen == "AbilitySingleplayer": 
        abilityButtonCheck(app.ship, x, y)
    elif app.screen == "AbilityMultiplayer": 
        sLst = ["x", "y", "f"]
        for s in sLst: 
            abilityButtonCheck(s, x, y)
    if levelScreenGroup.hits(x, y) and app.screen == "Level": 
        level = 0
        for i in levelScreenGroup: 
            i.chosen = False
            if app.highestLevel >= level or level == 15: 
                changeBorderColor(i, 'gold')
                if i.hits(x, y): 
                    i.chosen = True
                    app.level = level
                    changeBorderColor(i, 'red')
            level += 1
    if app.screen == "ChooseShip": 
        for i in choosingGroup: 
            changeBorderColor(i, 'aqua')
            if i.hits(x, y): 
                app.ship = shipChooseDict[i]
                changeBorderColor(i, 'red')
    if continueControlScreen.hits(x, y): 
        if app.screen == "multiplayer": 
            app.screen = "AbilityMultiplayer"
            abilityChooseGroupY.visible = True
            abilityChooseGroupY.centerY = 200*app.sizeMulti
            abilityChooseGroupX.visible = True
            abilityChooseGroupF.centerY = 100*app.sizeMulti
            abilityChooseGroupF.visible = True
            abilityChooseGroupY.centerX = 250*app.sizeMulti
            abilityChooseGroupX.centerX = 250*app.sizeMulti
            abilityChooseGroupF.centerX = 250*app.sizeMulti
        if app.screen == "soloControls": 
            app.screen = "ChooseShip"
        if (app.ship != "z" and app.screen == "ChooseShip") or app.screen == "multiplayer": 
            sLst = ["x", "y", "f"]
            for s in sLst: 
                changeBorderColor(abilityChooseButtonDict[s], 'aqua')
                changeBorderColor(abilityChooseLabelDict[s], 'aqua')
                abilityDict[s] = "N"
            abilityChooseScreenDict[app.ship].visible = True
            abilityChooseScreenDict[app.ship].centerY = 300*app.sizeMulti
            abilityChooseScreenDict[app.ship].centerX = 200*app.sizeMulti
            app.screen = "AbilitySingleplayer"
        if app.screen == "AbilitySingleplayer" and abilityDict[app.ship] != "N": 
            if app.ship == "x": 
                if abilityDict["x"] == "xs": 
                    XWing(80*app.sizeMulti, 200*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', supportEnabled = True)
                else: 
                    XWing(80*app.sizeMulti, 200*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', dashEnabled = True)
            elif app.ship == 'y': 
                if abilityDict["y"] == "yb": 
                    YWing(80*app.sizeMulti, 200*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', bomb = True)
                elif abilityDict["y"] == "ye": 
                    YWing(80*app.sizeMulti, 200*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', emp = True)
                else: 
                    YWing(80*app.sizeMulti, 200*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', cluster = True)
            elif app.ship == 'f': 
                if abilityDict["f"] == "fa": 
                    Falcon(80*app.sizeMulti, 200*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', autoAimEnabled = True)
                else: 
                    Falcon(80*app.sizeMulti, 200*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', healthRegenEnabled = True)
            start()
        elif app.screen == "AbilityMultiplayer" and abilityDict["x"] != "N" and abilityDict["f"] != "N" and abilityDict["y"] != "N": 
            if abilityDict["x"] == "xs": 
                XWing(80*app.sizeMulti, 300*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', supportEnabled = True)
            else: 
                XWing(80*app.sizeMulti, 300*app.sizeMulti, 'up', 'down', 'right', 'left', 'space', 'c', dashEnabled = True)
            if abilityDict["y"] == "yb": 
                YWing(80*app.sizeMulti, 200*app.sizeMulti, 'w', 's', 'd', 'a', 'q', 'e', bomb = True)
            elif abilityDict["y"] == "ye": 
                YWing(80*app.sizeMulti, 200*app.sizeMulti, 'w', 's', 'd', 'a', 'q', 'e', emp = True)
            else: 
                YWing(80*app.sizeMulti, 200*app.sizeMulti, 'w', 's', 'd', 'a', 'q', 'e', cluster = True)
            if abilityDict["f"] == "fa": 
                Falcon(80*app.sizeMulti, 100*app.sizeMulti, 'i', 'k', 'l', 'j', 'u', 'o', autoAimEnabled = True)
            else: 
                Falcon(80*app.sizeMulti, 100*app.sizeMulti, 'i', 'k', 'l', 'j', 'u', 'o', healthRegenEnabled = True)
            app.level = 18
            start()
        if app.screen == "Level": 
            levelSelected = False
            for i in levelScreenGroup: 
                if i.chosen: 
                    levelSelected = True
            if levelSelected: 
                app.numPlayers = 1
                app.screen = "soloControls"
    if app.screen == "Home": 
        if solo.hits(x, y): 
            level = 0
            for i in levelScreenGroup: 
                if level <= app.highestLevel or level == 15: 
                    changeBorderColor(i, 'gold')
                level += 1
            app.screen = "Level"
        if multiplayer.hits(x, y): 
            app.numPlayers = 2
            app.screen = "multiplayer"
        if upgradeButton.hits(x, y): 
            upgradeShips()
        if importButton.hits(x, y): 
            importSaveCode()
        if exportButton.hits(x, y): 
            exportSaveCode()
    if (retry.hits(x, y) and app.screen == "RetryLoseSingleplayer") or (winContinue.hits(x, y) and app.screen == "ContinueWin"): 
        reset()
    if (leaderboardContinue.hits(x, y) and app.screen == "LeaderBoard"): 
        reset()
        app.round += 1
    if continueNd.hits(x, y) and app.screen == "RetryLoseMultiplayer": 
        app.screen = "LeaderBoard"
# removes all non-number characters from a string except -
def filterString(string): 
    numLst = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "."]
    newstring1 = ""
    for c in string: 
        if c in numLst: 
            newstring1 += c
    if len(newstring1) > 1: 
        newstring2 = ""
        for i in range(1, len(newstring1)): 
            if i == 1 or newstring1[i] != "-": 
                newstring2 += newstring1[i]
        return newstring2
    return newstring1
# improved str to int
def changeToInt(string): 
    if len(string) > 1: 
        if string[0] == "-": 
            newstring = ""
            for c in range(1, len(string)): 
                newstring += string[c]
            return -int(newstring)
    return int(string)
def changeToFloat(string): 
    if len(string) > 1: 
        if string[0] == "-": 
            newstring = ""
            for c in range(1, len(string)): 
                newstring += string[c]
            return -float(newstring)
    return float(string)
def filterAndFloat(string): 
    return changeToFloat(filterString(string))
def filterAndInt(string): 
    return changeToInt(filterString(string))
# upgrade prompts
def getUpgradeAmountF(upgradeNum, u): 
    return filterString(
        "0"+app.getTextInput(
            "Upgrade Falcon "+upgradeNum+" (Current "+upgradeNum+" Boost: "+str(Falcon.boostLst[u])+
            ", "+upgradeNum+" Upgrades: "+str(app.boostLst[u])+") by: "
        )
    )
def upgradePromptF(upgradeNum, u): 
    upgradeAmount = getUpgradeAmountF(upgradeNum, u)
    while len(upgradeAmount) == 0: 
        upgradeAmount = getUpgradeAmountF(upgradeNum, u)
    return changeToInt(upgradeAmount)
def getAbilityUpgradeAmountF(upgradeNum, u): 
    return filterString(
        "0"+app.getTextInput(
            "Upgrade Falcon "+upgradeNum+" (Current "+upgradeNum+" Boost: "+str(Falcon.abilityBoostLst[u])+
            ", "+upgradeNum+" Upgrades: "+str(app.abilityBoostLstF[u])+") by: "
        )
    )
def abilityUpgradePromptF(upgradeNum, u): 
    upgradeAmount = getAbilityUpgradeAmountF(upgradeNum, u)
    while len(upgradeAmount) == 0: 
        upgradeAmount = getAbilityUpgradeAmountF(upgradeNum, u)
    return changeToInt(upgradeAmount)
def getUpgradeAmountX(upgradeNum, u): 
    return filterString(
        "0"+app.getTextInput(
            "Upgrade X-Wing "+upgradeNum+" (Current "+upgradeNum+" Boost: "+str(XWing.boostLst[u])+
            ", "+upgradeNum+" Upgrades: "+str(app.boostLst[u])+") by: "
        )
    )
def upgradePromptX(upgradeNum, u): 
    upgradeAmount = getUpgradeAmountX(upgradeNum, u)
    while len(upgradeAmount) == 0: 
        upgradeAmount = getUpgradeAmountX(upgradeNum, u)
    return changeToInt(upgradeAmount)
def getAbilityUpgradeAmountX(upgradeNum, u): 
    return filterString(
        "0"+app.getTextInput(
            "Upgrade X-Wing "+upgradeNum+" (Current "+upgradeNum+" Boost: "+str(XWing.abilityBoostLst[u])+
            ", "+upgradeNum+" Upgrades: "+str(app.abilityBoostLstX[u])+") by: "
        )
    )
def abilityUpgradePromptX(upgradeNum, u): 
    upgradeAmount = getAbilityUpgradeAmountX(upgradeNum, u)
    while len(upgradeAmount) == 0: 
        upgradeAmount = getAbilityUpgradeAmountX(upgradeNum, u)
    return changeToInt(upgradeAmount)
def getUpgradeAmountY(upgradeNum, u): 
    return filterString(
        "0"+app.getTextInput(
            "Upgrade Y-Wing "+upgradeNum+" (Current "+upgradeNum+" Boost: "+str(YWing.boostLst[u])+
            ", "+upgradeNum+" Upgrades: "+str(app.boostLst[u])+") by: "
        )
    )
def upgradePromptY(upgradeNum, u): 
    upgradeAmount = getUpgradeAmountY(upgradeNum, u)
    while len(upgradeAmount) == 0: 
        upgradeAmount = getUpgradeAmountY(upgradeNum, u)
    return changeToInt(upgradeAmount)
def getAbilityUpgradeAmountY(upgradeNum, u): 
    return filterString(
        "0"+app.getTextInput(
            "Upgrade Y-Wing "+upgradeNum+" (Current "+upgradeNum+" Boost: "+str(YWing.abilityBoostLst[u])+
            ", "+upgradeNum+" Upgrades: "+str(app.abilityBoostLstY[u])+") by: "
        )
    )
def abilityUpgradePromptY(upgradeNum, u): 
    upgradeAmount = getAbilityUpgradeAmountY(upgradeNum, u)
    while len(upgradeAmount) == 0: 
        upgradeAmount = getAbilityUpgradeAmountY(upgradeNum, u)
    return changeToInt(upgradeAmount)
def upgradeShips(): 
    upgradeShip = app.getTextInput("Input 'x': Upgrade X-Wing, 'y': Upgrade Y-Wing, 'f': Upgrade Falcon")
    if upgradeShip.lower() == "f": 
        for u in range(len(app.boostLst)): 
            if app.boostLst[u] != 0 or Falcon.boostLst[u] != 0: 
                upgradeNum = app.lst[u]
                upgradeAmount = upgradePromptF(upgradeNum, u)
                while (
                    app.boostLst[u]-upgradeAmount < 0 or 
                    (u == 1 and Falcon.boostLst[1]+upgradeAmount > 50) or 
                    (u == 4 and Falcon.boostLst[4]+upgradeAmount > 12) or 
                    Falcon.boostLst[u]+upgradeAmount < 0
                ): 
                    app.getTextInput("Not Enough Upgrades/Used Too Many Upgrades")
                    upgradeAmount = upgradePromptF(upgradeNum, u)
                app.boostLst[u] -= upgradeAmount
                Falcon.boostLst[u] += upgradeAmount
        for u in range(len(Falcon.abilityBoostLst)): 
            if app.abilityBoostLstF[u] != 0 or Falcon.abilityBoostLst[u] != 0: 
                upgradeNum = Falcon.abilityBoostNameLst[u]
                upgradeAmount = abilityUpgradePromptF(upgradeNum, u)
                while (
                    app.abilityBoostLstF[u]-upgradeAmount < 0 or 
                    (u == 0 and Falcon.abilityBoostLst[0]+upgradeAmount > 8) or 
                    Falcon.abilityBoostLst[u]+upgradeAmount < 0
                ): 
                    app.getTextInput("Not Enough Upgrades/Used Too Many Upgrades")
                    upgradeAmount = abilityUpgradePromptF(upgradeNum, u)
                app.abilityBoostLstF[u] -= upgradeAmount
                Falcon.abilityBoostLst[u] += upgradeAmount
    elif upgradeShip.lower() == "x": 
        for u in range(len(app.boostLst)): 
            if (app.boostLst[u] != 0 or XWing.boostLst[u] != 0) and u != 1: 
                upgradeNum = app.lst[u]
                upgradeAmount = upgradePromptX(upgradeNum, u)
                while (
                    app.boostLst[u]-upgradeAmount < 0 or 
                    (u == 4 and XWing.boostLst[4]+upgradeAmount > 14) or 
                    XWing.boostLst[u]+upgradeAmount < 0
                ): 
                    app.getTextInput("Not Enough Upgrades/Used Too Many Upgrades")
                    upgradeAmount = upgradePromptX(upgradeNum, u)
                app.boostLst[u] -= upgradeAmount
                XWing.boostLst[u] += upgradeAmount
        for u in range(len(XWing.abilityBoostLst)): 
            if app.abilityBoostLstX[u] != 0 or XWing.abilityBoostLst[u] != 0: 
                upgradeNum = XWing.abilityBoostNameLst[u]
                upgradeAmount = abilityUpgradePromptX(upgradeNum, u)
                while (
                    app.abilityBoostLstX[u]-upgradeAmount < 0 or 
                    (u == 0 and XWing.abilityBoostLst[0]+upgradeAmount > 4) or 
                    (u == 4 and XWing.abilityBoostLst[4]+upgradeAmount > 15) or 
                    (u == 1 and XWing.abilityBoostLst[1]+upgradeAmount > 10) or 
                    (u == 3 and XWing.abilityBoostLst[3]+upgradeAmount > 49) or 
                    XWing.abilityBoostLst[u]+upgradeAmount < 0
                ): 
                    app.getTextInput("Not Enough Upgrades/Used Too Many Upgrades")
                    upgradeAmount = abilityUpgradePromptX(upgradeNum, u)
                app.abilityBoostLstX[u] -= upgradeAmount
                XWing.abilityBoostLst[u] += upgradeAmount
    elif upgradeShip.lower() == "y": 
        for u in range(len(app.boostLst)): 
            if app.boostLst[u] != 0 or YWing.boostLst[u] != 0: 
                upgradeNum = app.lst[u]
                upgradeAmount = upgradePromptY(upgradeNum, u)
                while (
                    app.boostLst[u]-upgradeAmount < 0 or 
                    (u == 1 and YWing.boostLst[1]+upgradeAmount > 40) or 
                    (u == 4 and YWing.boostLst[4]+upgradeAmount > 30) or 
                    YWing.boostLst[u]+upgradeAmount < 0
                ): 
                    app.getTextInput("Not Enough Upgrades/Used Too Many Upgrades")
                    upgradeAmount = upgradePromptY(upgradeNum, u)
                app.boostLst[u] -= upgradeAmount
                YWing.boostLst[u] += upgradeAmount
        for u in range(len(YWing.abilityBoostLst)): 
            if app.abilityBoostLstY[u] != 0 or YWing.abilityBoostLst[u] != 0: 
                upgradeNum = YWing.abilityBoostNameLst[u]
                upgradeAmount = abilityUpgradePromptY(upgradeNum, u)
                while (
                    app.abilityBoostLstY[u]-upgradeAmount < 0 or 
                    (u == 0 and YWing.abilityBoostLst[0]+upgradeAmount > 6) or 
                    (u == 2 and YWing.abilityBoostLst[2]+upgradeAmount > 15) or 
                    YWing.abilityBoostLst[u]+upgradeAmount < 0 or
                    (u == 8 and YWing.abilityBoostLst[8]+upgradeAmount > 70) or 
                    (u == 9 and YWing.abilityBoostLst[u]+upgradeAmount > 50)
                ): 
                    app.getTextInput("Not Enough Upgrades/Used Too Many Upgrades")
                    upgradeAmount = abilityUpgradePromptY(upgradeNum, u)
                app.abilityBoostLstY[u] -= upgradeAmount
                YWing.abilityBoostLst[u] += upgradeAmount
# save functions
def saveUpgrades(lst, string): 
    string += "|"
    for upgrade in lst: 
        string += str(upgrade)
        string += "."
    newstring = ""
    for i in range(len(string)-1): 
        newstring += string[i]
    return newstring
def importSaveCode(): 
    # savedCode = app.getTextInput("Input Code: ")
    savedCode = input("Input Code: ")
    if len(savedCode) != 0: 
        codes = savedCode.split("|")
        upgradeCodes = []
        a = 0
        for code in codes: 
            if a != 0: 
                upgradeCodes.append(code)
            a += 1
        app.highestLevel = int(upgradeCodes[0])
        applst = upgradeCodes[1].split(".")
        for u in range(len(applst)): 
            app.boostLst[u] += int(applst[u])
        xwingLst = upgradeCodes[2].split(".")
        for u in range(len(xwingLst)): 
            XWing.boostLst[u] += int(xwingLst[u])
        ywingLst = upgradeCodes[3].split(".")
        for u in range(len(ywingLst)): 
            YWing.boostLst[u] += int(ywingLst[u])
        falconLst = upgradeCodes[4].split(".")
        for u in range(len(falconLst)): 
            Falcon.boostLst[u] += int(falconLst[u])
        appAbilityUpgradeXLst = upgradeCodes[5].split(".")
        for u in range(len(appAbilityUpgradeXLst)): 
            app.abilityBoostLstX[u] += int(appAbilityUpgradeXLst[u])
        appAbilityUpgradeYLst = upgradeCodes[6].split(".")
        for u in range(len(appAbilityUpgradeYLst)): 
            app.abilityBoostLstY[u] += int(appAbilityUpgradeYLst[u])
        appAbilityUpgradeFLst = upgradeCodes[7].split(".")
        for u in range(len(appAbilityUpgradeFLst)): 
            app.abilityBoostLstF[u] += int(appAbilityUpgradeFLst[u])
        abilityUpgradeXLst = upgradeCodes[8].split(".")
        for u in range(len(abilityUpgradeXLst)): 
            XWing.abilityBoostLst[u] += int(abilityUpgradeXLst[u])
        abilityUpgradeYLst = upgradeCodes[9].split(".")
        for u in range(len(abilityUpgradeYLst)): 
            YWing.abilityBoostLst[u] += int(abilityUpgradeYLst[u])
        abilityUpgradeFLst = upgradeCodes[10].split(".")
        for u in range(len(abilityUpgradeFLst)): 
            Falcon.abilityBoostLst[u] += int(abilityUpgradeFLst[u])
def exportSaveCode(): 
    saveCode = "|"+str(app.highestLevel)
    saveCode = saveUpgrades(app.boostLst, saveCode)
    saveCode = saveUpgrades(XWing.boostLst, saveCode)
    saveCode = saveUpgrades(YWing.boostLst, saveCode)
    saveCode = saveUpgrades(Falcon.boostLst, saveCode)
    saveCode = saveUpgrades(app.abilityBoostLstX, saveCode)
    saveCode = saveUpgrades(app.abilityBoostLstY, saveCode)
    saveCode = saveUpgrades(app.abilityBoostLstF, saveCode)
    saveCode = saveUpgrades(XWing.abilityBoostLst, saveCode)
    saveCode = saveUpgrades(YWing.abilityBoostLst, saveCode)
    saveCode = saveUpgrades(Falcon.abilityBoostLst, saveCode)
    #app.getTextInput(saveCode)
    print(saveCode)
# onKey Functions
def onKeyPress(key): 
    # allows more than two held down keys to be tracked at once
    if key not in app.keys: 
        app.keys.append(key)
    # saving and loading upgrades
    if key == '0': # displays save code
        exportSaveCode()
    elif key == '9': # gets save code, loads upgrades based on code
        importSaveCode()
    elif key == '8': # asks what to upgrade
        upgradeShips()
    # cheats
    elif key == '7': 
        app.score = int("0"+app.getTextInput("Set Score to: "))
    elif key == '5': # sets cooldowns and Mxes
        app.tFCap = int("0"+app.getTextInput("Set Tie-Fighter Cap to: "))
        app.tFCooldown = int("0"+app.getTextInput("Set Tie-Fighter Cooldown to: "))
        app.asteroidCap = int("0"+app.getTextInput("Set Asteroid Cap to: "))
        app.asteroidRate = int("0"+app.getTextInput("Set Asteroid Rate to: "))
        app.tBCap = int("0"+app.getTextInput("Set Tie-Bomber Cap to: "))
        app.tBCooldown = int("0"+app.getTextInput("Set Tie-Bomber Cooldown to: "))
        app.sDCap = int("0"+app.getTextInput("Set Star Destroyer Cap to: "))
        app.sDCooldown = int("0"+app.getTextInput("Set Star Destroyer Cooldown to: "))
    # spawns new hazards
    elif key == '4': 
        Asteroid()
    elif key == '3': 
        TieFighter(randrange(20, 381))
    elif key == '2': 
        TieBomber(randrange(20, 381))
    elif key == '1': 
        StarDestroyer(randrange(25, 391))
    elif key == ' = ': # adds a random Upgrade
        if randrange(0, 11) == 10: 
            au = randrange(0, 3)
            if au == 0: 
                app.abilityBoostLstX[randrange(0, len(app.abilityBoostLstX))] += 1
            elif au == 1: 
                app.abilityBoostLstY[randrange(0, len(app.abilityBoostLstY))] += 1
            else: 
                app.abilityBoostLstF[randrange(0, len(app.abilityBoostLstF))] += 1
        else: 
            app.boostLst[randrange(0, 10)] += 1
    elif key == '+': # gives an amount of random Upgrades
        u = int("0"+app.getTextInput("Give how many upgrades: "))
        for i in range(u): 
            onKeyPress(' = ')
    elif key == '-': # clears the screen
        clearscreen()
    if key == '`': 
        asteroidAmountn = filterAndFloat("0"+app.getTextInput("Asteroid Amount: "))
        tFAmountn = filterAndFloat("0"+app.getTextInput("Tie-Fighter Amount: "))
        tBAmountn = filterAndFloat("0"+app.getTextInput("Tie-Bomber Amount: "))
        sDAmountn = filterAndFloat("0"+app.getTextInput("Star Destroyer Amount: "))
        asteroidSpawnRateModn = filterAndFloat("0"+app.getTextInput("Asteroid Spawn Mod: "))
        tFSpawnRateModn = filterAndFloat("0"+app.getTextInput("Tie-Fighter Spawn Mod: "))
        tBSpawnRateModn = filterAndFloat("0"+app.getTextInput("Tie-Bomber Spawn Mod: "))
        sDSpawnRateModn = filterAndFloat("0"+app.getTextInput("Star Destroyer Spawn Mod: "))
        asteroidCapModn = filterAndFloat("0"+app.getTextInput("Asteroid Cap Mod: "))
        tFCapModn = filterAndFloat("0"+app.getTextInput("Tie-Fighter Cap Mod: "))
        tBCapModn = filterAndFloat("0"+app.getTextInput("Tie-Bomber Cap Mod: "))
        sDCapModn = filterAndFloat("0"+app.getTextInput("Star Destroyer Cap Mod: "))
        Level.levelLst.remove(Level.levelLst[15])
        Level(
            tFAmount = tFAmountn, 
            asteroidAmount = asteroidAmountn, 
            tBAmount = tBAmountn, 
            sDAmount = sDAmountn, 
            tFSpawnRateMod = tFSpawnRateModn, 
            tBSpawnRateMod = tBSpawnRateModn, 
            asteroidSpawnRateMod = asteroidSpawnRateModn, 
            sDSpawnRateMod = sDSpawnRateModn, 
            asteroidCapMod = asteroidCapModn, 
            tFCapMod = tFCapModn, 
            tBCapMod = tBCapModn, 
            sDCapMod = sDCapModn
        )
    if key == '~': 
        app.asteroidSizeMod = filterAndInt("0"+app.getTextInput("Asteroid Size Cap: "))
        app.enemyHPMod = filterAndInt("0"+app.getTextInput("Enemy HP Mod: "))
        app.enemyCooldownMod = filterAndInt("0"+app.getTextInput("Enemy Cooldown Mod: "))
        app.enemyDMGMod = filterAndInt("0"+app.getTextInput("Enemy Damage Mod: "))
    if app.numPlayers == 2 and backgroundAndTitle.visible: 
        leaderboardScreen(app.getTextInput())
def onKeyHold(keys): 
    keys.clear()
def onKeyRelease(key): 
    if key in app.keys: 
        app.keys.remove(key)
cmu_graphics.run()