import bs
import random
import math
import weakref

def bsGetAPIVersion():
	return 4

def bsGetGames():
	return [FinalCSMPGameBeta]

def bsGetLevels():
	# Levels are unique named instances of a particular game with particular settings.
	# They show up as buttons in the co-op section, get high-score lists associated with them, etc.
	return [bs.Level('FinalCSMPGameBeta', # globally-unique name for this level (not seen by user)
			displayName='${GAME}', # ${GAME} will be replaced by the results of the game's getName() call
			gameType=FinalCSMPGameBeta,
			settings={}, # we currently dont have any settings; we'd specify them here if we did.
			previewTexName='courtyardPreview')]

class FinalCSMPGameBeta(bs.CoopGameActivity):
    @classmethod
    def getName(cls):
        return 'Final CSMP (Beta)'

    @classmethod
    def getDescription(cls,sessionType):
        return "Este es el Final? "

    def __init__(self,settings={}):

        settings['map'] = 'Courtyard'

        bs.CoopGameActivity.__init__(self,settings)

        # show messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
        self._specialWaveSound = bs.getSound('dingSmall')
        self._newWaveSound = bs.getSound('scoreHit01')
        self._winSound = bs.getSound("score")
        self._cashRegisterSound = bs.getSound('cashRegister')
        self._aPlayerHasBeenHurt = False
        self._playerHasDroppedBomb = False

        # fixme - should use standard map defs..
        self._spawnCenter = (0,3,-2)
        self._tntSpawnPosition = (0,3,2.1)
        self._powerupCenter = (0,5,-1.6)
        self._powerupSpread = (4.6,2.7)
        

    def onTransitionIn(self):

        bs.CoopGameActivity.onTransitionIn(self)
        self._spawnInfoText = bs.NodeActor(bs.newNode("text",
                                                      attrs={'position':(15,-130),
                                                             'hAttach':"left",
                                                             'vAttach':"top",
                                                             'scale':0.55,
                                                             'color':(0.3,0.8,0.3,1.0),
                                                             'text':'>>>'}))
        bs.playMusic('Onslaught')

        self._scoreBoard = bs.ScoreBoard(label=bs.Lstr(resource='scoreText'),scoreSplit=0.5)
        self._gameOver = False
        self._wave = 0
        self._canEndWave = True
        self._score = 0
        self._timeBonus = 0


    def onBegin(self):
        bs.CoopGameActivity.onBegin(self)
        playerCount = len(self.players)
        #bsUtils.animateArray(bs.getSharedObject('globals'),'vignetteOuter',3,{0:(1,1.2,1.1),250:(1,0,0),500:(1,1.2,1.1),750:(1,1.2,1.1)},True) #No funciona
        bs.getSharedObject('globals').ambientColor = (1,1,1)
        bs.getSharedObject('globals').vignetteOuter = (0.8,0.8,0.8)
        bs.getSharedObject('globals').vignetteInner = (0.8,0.8,0.8)
        self._dingSound = bs.getSound('dingSmall')
        self._dingSoundHigh = bs.getSound('dingSmallHigh')
        
        import bsUtils
        bsUtils.ControlsHelpOverlay(delay=3000,lifespan=10000,bright=True).autoRetain()

        self._haveTnt = False
        self._excludePowerups = []
        self._waves = [
                #1 #Primera Horda, dando a conocer lo que se aproxima.
                {'entries':[
                        {'type':bs.OsoMatonBot,'point':'Left'},
                        {'type':bs.DAVRBot,'point':'Right'},
                        {'type':bs.OsaMatonaBot,'point':'BottomRight'} if playerCount > 1 else None,
                        {'type':bs.OsoEspectroBot,'point':'BottomLeft'} if playerCount > 2 else None,
                        {'type':bs.CelyBot,'point':'Top'},
                        {'type':bs.OsoCulionBot,'point':'Bottom'},
                        ]},
                #2 #El brillo de el terror! XDXD
                {'entries':[
                        {'type':bs.NeonBot,'point':'Left'},
                        {'type':bs.Neon2Bot,'point':'Right'},
                        {'type':bs.BearBotPro,'point':'Top'},
                        {'type':bs.BearBot,'point':'Bottom'},
                        {'type':bs.BearBot,'point':'BottomRight'} if playerCount > 1 else None,
                        {'type':bs.BearBotPro,'point':'BottomLeft'} if playerCount > 1 else None,
                        {'type':bs.NeonBot,'point':'TopLeft'} if playerCount > 2 else None,
                        {'type':bs.Neon3Bot,'point':'TopRight'} if playerCount > 2 else None,
                        {'type':bs.EggBot,'point':'TurretTopMiddle'},
                        ]},
                #3 #Bichos Helados o congelados.
                {'entries':[
                        {'type':bs.FrostyBot,'point':'TopRight'},
                        {'type':bs.FrostyBot,'point':'RightUpper'}, 
                        {'type':bs.FrostyBotPro,'point':'RightLower'} if playerCount > 1 else None,
                        {'type':bs.FrostyBotProShielded,'point':'RightLowerMore'} if playerCount > 2 else None,
                        {'type':bs.FrostyBotPro,'point':'BottomRight'},
                        {'type':bs.FrostyBotPro,'point':'Right'},
                        {'type':'delay','duration':6000},
                        {'type':bs.PascalBot,'point':'Right'},
                        {'type':bs.PascalBot,'point':'Left'},
                        ]},
                #4 #Se viene algo magico :v!
                {'entries':[
                        {'type':bs.WizardBot,'point':'TurretTopMiddleRight'},
                        {'type':bs.WizardBotPro,'point':'TurretTopMiddleLeft'},
                        {'type':bs.NoFrostyBot,'point':'RightUpperMore'} if playerCount > 1 else None,
                        {'type':bs.NoFrostyBot,'point':'RightUpper'}, 
                        {'type':bs.BonesBot,'point':'Top'}, 
                        {'type':bs.NoFrostyBot,'point':'RightLower'},
                        {'type':bs.BonesBot,'point':'RightLowerMore'} if playerCount > 2 else None,
                        {'type':bs.BonesBot,'point':'BottomRight'},
                        {'type':bs.BearBotPro,'point':'TopRight'},
                        ]},
                #5 #Que empieze la locura!!
                {'entries':[
                		{'type':bs.NoFrostyBot,'point':'TurretTopRight'},
                		{'type':bs.NoFrostyBot,'point':'TurretTopMiddle'},
                        {'type':bs.NoFrostyBot,'point':'TurretTopLeft'},
                        {'type':bs.NoFrostyBot,'point':'TurretBottomLeft'},
                        {'type':bs.NoFrostyBot,'point':'TurretBottomRight'},
                        {'type':bs.NoFrostyBot,'point':'BottomRight'} if playerCount > 1 else None,
                        {'type':bs.BearBot,'point':'Right'}, 
                        {'type':bs.BearBot,'point':'Left'},
                        {'type':bs.NoFrostyBot,'point':'BottomLeft'},
                        {'type':bs.NoFrostyBot,'point':'TopRight'} if playerCount > 2 else None,
                        {'type':bs.NoFrostyBot,'point':'Bottom'},
                        {'type':bs.EggBot,'point':'Top'},
                        ]},
                #6 #Esto es de locos!
                {'entries':[
                		{'type':bs.MostroBot,'point':'Right'},
                		{'type':bs.MostroBotPro,'point':'Top'},
                        {'type':bs.MostroBot,'point':'Left'},
                        {'type':bs.MostroBot,'point':'Top'} if playerCount > 1 else None,
                        {'type':bs.MostroBotPro,'point':'Bottom'} if playerCount > 2 else None,
                        ]},
                #7 #Estar cerca nunca es bueno, y menos que mueran junto a ti
                {'entries':[
                		{'type':bs.SuicideBot,'point':'Right'},
                		{'type':bs.SuicideBomberBot,'point':'TurretTopMiddle'},
                        {'type':bs.SuicideBot,'point':'Left'},
                        {'type':'delay','duration':4000},
                        {'type':bs.SuicideBot,'point':'Top'},
                        {'type':bs.SuicideBot,'point':'Bottom'},
                        {'type':bs.SuicideBot,'point':'BottomLeft'} if playerCount > 1 else None,
                        {'type':bs.SuicideBot,'point':'BottomRight'} if playerCount > 1 else None,
                        {'type':bs.SuicideBot,'point':'TopRight'} if playerCount > 2 else None,
                        {'type':bs.SuicideBot,'point':'TopLeft'} if playerCount > 2 else None,
                        ]},               	
                #8 #Ataque de locos!?
                {'entries':[
                		{'type':bs.MostroBot,'point':'Left'},
                		{'type':bs.MostroBot,'point':'Right'},
                		{'type':bs.BonesBot,'point':'BottomLeft'},
                		{'type':bs.BonesBot,'point':'BottomRight'},
                		{'type':bs.NoFrostyBot,'point':'TopLeft'},
                		{'type':bs.NoFrostyBot,'point':'TopRight'},
                		{'type':bs.EggBot,'point':'Top'},
                        {'type':bs.EggBot,'point':'Bottom'},
                        {'type':bs.NeonBot,'point':'TurretBottomLeft'},
                        {'type':bs.Neon2Bot,'point':'TurretBottomRight'},
                        {'type':bs.Neon3Bot,'point':'TurretTopMiddle'},
                        ]},
                #9 #que carajos? son putinas!.
                {'entries':[
                		{'type':bs.PutininBot,'point':'Top'},
                        {'type':'delay','duration':500},
                		{'type':bs.PutininBot,'point':'Top'},
                        {'type':'delay','duration':500},
                		{'type':bs.PutininBot,'point':'Top'},
                        {'type':'delay','duration':500},
                        {'type':bs.PutininBot,'point':'Top'},
                        {'type':'delay','duration':500},
                        {'type':bs.PutininBot,'point':'Top'},
                        {'type':'delay','duration':500},
                        {'type':bs.PutininBot,'point':'Top'},
                        {'type':'delay','duration':500},
                        {'type':bs.BearBotPro,'point':'Right'},
                        {'type':bs.BearBotPro,'point':'Left'},
                        {'type':bs.BearBotPro,'point':'Top'},
                        {'type':bs.BearBotPro,'point':'Bottom'} if playerCount > 1 else None,
                        {'type':bs.BearBotPro,'point':'BottomLeft'} if playerCount > 2 else None,
                        {'type':'delay','duration':2000},
                        {'type':bs.PutininBot,'point':'Top'},
                        {'type':bs.NoFrostyBot,'point':'Left'},
                        {'type':bs.NoFrostyBot,'point':'Right'},
                        {'type':bs.NoFrostyBot,'point':'Bottom'},
                        {'type':'delay','duration':5000},
                        {'type':bs.MostroBot,'point':'Top'},
                        {'type':bs.MostroBot,'point':'Left'},
                        {'type':bs.MostroBotPro,'point':'Right'},
                        {'type':bs.MostroBotPro,'point':'Bottom'},
                        {'type':'delay','duration':8000},
                        {'type':bs.SuicideBot,'point':'Top'},
                        {'type':bs.SuicideBot,'point':'Left'},
                        {'type':bs.SuicideBot,'point':'Right'},
                        {'type':bs.SuicideBot,'point':'Bottom'},
                        ]},
                #10 #Frio V2
                {'entries':[
                		{'type':bs.PascalBot,'point':'Top'},
                        {'type':bs.FrostyBotPro,'point':'TurretBottomLeft'},
                        {'type':bs.FrostyBotPro,'point':'TurretBottomRight'},
                        {'type':bs.FrostyBotPro,'point':'TurretTopRight'},
                        {'type':bs.FrostyBotPro,'point':'TurretTopLeft'},
                        {'type':bs.FrostyBotProShielded,'point':'TurretTopMiddleLeft'},
                        {'type':bs.FrostyBotProShielded,'point':'TurretTopMiddleRight'},
                        {'type':bs.PascalBot,'point':'Left'},
                        {'type':bs.PascalBot,'point':'Right'},
                        ]},
                #11 #Una pizca de tnt congelada
                {'entries':[
                		{'type':bs.MostroBot,'point':'TurretTopMiddle'},
                        {'type':bs.BonesBot,'point':'Bottom'},
                        {'type':bs.NoFrostyBot,'point':'Left'},
                        {'type':bs.NoFrostyBot,'point':'Right'},
                        {'type':bs.BonesBot,'point':'Top'},
                        {'type':'delay','duration':5000},
                        {'type':bs.BearBot,'point':'Right'},
                        {'type':bs.BearBot,'point':'Left'},
                        {'type':'delay','duration':7000},
                        {'type':bs.SuicideBomberBot,'point':'TurretBottomLeft'},
                        {'type':bs.FrostyBot,'point':'TurretBottomRight'},
                        {'type':bs.SuicideBomberBot,'point':'TurretTopRight'},
                        {'type':bs.FrostyBot,'point':'TurretTopLeft'},
                        {'type':'delay','duration':15000},
                        {'type':bs.EggBot,'point':'Left'},
                        {'type':bs.SuicideBot,'point':'Right'},
                        ]},
                      #12 #Jefe final
                {'entries':[
                		{'type':bs.CelyBot,'point':'Top'},
                        {'type':bs.OsoCulionBot,'point':'Bottom'},
                        {'type':bs.DAVRBot,'point':'Left'},
                        {'type':'delay','duration':3000},
                        {'type':bs.MostroBot,'point':'TurretBottomRight'},
                		{'type':bs.EggBot,'point':'TurretTopMiddle'},
                		{'type':bs.MostroBotPro,'point':'TurretBottomLeft'},
                		{'type':bs.MostroBot,'point':'TurretTopLeft'},
                		{'type':bs.MostroBotPro,'point':'TurretTopRight'},
                		{'type':'delay','duration':6000},
                		{'type':bs.NoFrostyBot,'point':'Right'},
                		{'type':bs.NoFrostyBot,'point':'Bottom'},
                		{'type':bs.NoFrostyBot,'point':'Left'},
                		{'type':'delay','duration':10000},
                		{'type':bs.BonesBot,'point':'Left'},
                		{'type':bs.BonesBot,'point':'LeftUpper'},
                		{'type':bs.NeonBot,'point':'RightUpper'},
                		{'type':bs.NeonBot,'point':'RightLower'},
                		{'type':bs.Neon2Bot,'point':'LeftLower'},
                		{'type':bs.Neon2Bot,'point':'Right'},
                		{'type':bs.Neon3Bot,'point':'Top'},
                		{'type':bs.Neon3Bot,'point':'Bottom'},
                		{'type':'delay','duration':13000},
                		{'type':bs.FrostyBotProShielded,'point':'TurretTopMiddleRight'},
                		{'type':bs.FrostyBotProShielded,'point':'TurretTopMiddleLeft'},
                		{'type':bs.FrostyBotProShielded,'point':'TurretTopMiddle'},
                		{'type':bs.PascalBot,'point':'LeftUpper'},
                		{'type':bs.PascalBot,'point':'LeftLower'},
                		{'type':bs.PascalBot,'point':'RightUpper'},
                		{'type':bs.PascalBot,'point':'RightLower'},
                		{'type':'delay','duration':15000},
                		{'type':bs.WizardBot,'point':'Bottom'},
                		{'type':bs.WizardBot,'point':'Top'},
                		{'type':bs.WizardBotPro,'point':'Left'},
                		{'type':bs.WizardBotPro,'point':'Right'},
                		{'type':'delay','duration':20000},
                		{'type':bs.BOSSBot,'point':'Top'},
                        {'type':'delay','duration':2000},
                        {'type':bs.DAVRBot,'point':'Right'},
                        {'type':bs.CelyBot,'point':'Left'},
                        {'type':bs.OsoCulionBot,'point':'Bottom'},
                		{'type':bs.OsoMatonBot,'point':'Top'},
                        {'type':'delay','duration':4000},
                        {'type':bs.DAVRBot,'point':'Right'},
                        {'type':'delay','duration':6000},
                        {'type':bs.CelyBot,'point':'Left'},
                        {'type':'delay','duration':8000},
                        {'type':bs.OsoCulionBot,'point':'Bottom'},
                        {'type':'delay','duration':10000},
                		{'type':bs.OsoMatonBot,'point':'Top'},
                        {'type':'delay','duration':12000},
                        {'type':bs.PascalBot,'point':'Bottom'},
                        {'type':bs.PascalBot,'point':'Bottom'},
                		]}
                ]
                
        self._dropPowerups(standardPoints=True,powerupType='curse')
        bs.gameTimer(4000,self._startPowerupDrops)
        if self._haveTnt:
            self._tntSpawner = bs.TNTSpawner(position=self._tntSpawnPosition)
        
        self.setupLowLifeWarningSound()
        
        self._updateScores()
        self._bots = bs.BotSet()

        bs.gameTimer(3500,self._startUpdatingWaves)


    def _onGotScoresToBeat(self,scores):
        self._showStandardScoresToBeatUI(scores)


    def _getDistribution(self,targetPoints,minDudes,maxDudes,groupCount,maxLevel):
        """ calculate a distribution of bad guys given some params """

        maxIterations = 10+maxDudes*2

        def _getTotals(grops):
            totalPoints = 0
            totalDudes = 0
            for group in groups:
                for entry in group:
                    dudes = entry[1]
                    totalPoints += entry[0]*dudes
                    totalDudes += dudes
            return totalPoints,totalDudes

        groups = []
        for g in range(groupCount):
            groups.append([])

        types = [1]
        if maxLevel > 1: types.append(2)
        if maxLevel > 2: types.append(3)
        if maxLevel > 3: types.append(4)

        for iteration in range(maxIterations):
            # see how much we're off our target by
            totalPoints,totalDudes = _getTotals(groups)
            diff = targetPoints - totalPoints
            dudesDiff = maxDudes - totalDudes
            # add an entry if one will fit
            value = types[random.randrange(len(types))]
            group = groups[random.randrange(len(groups))]
            if len(group) == 0: maxCount = random.randint(1,6)
            else: maxCount = 2*random.randint(1,3)
            maxCount = min(maxCount,dudesDiff)
            count = min(maxCount,diff/value)
            if count > 0:
                group.append((value,count))
                totalPoints += value*count
                totalDudes += count
                diff = targetPoints - totalPoints

            totalPoints,totalDudes = _getTotals(groups)
            full = (totalPoints >= targetPoints)

            if full:
                # every so often, delete a random entry just to shake up our distribution
                if random.random() < 0.2 and iteration != maxIterations-1:
                    entryCount = 0
                    for group in groups:
                        for entry in group:
                            entryCount += 1
                    if entryCount > 1:
                        delEntry = random.randrange(entryCount)
                        entryCount = 0
                        for group in groups:
                            for entry in group:
                                if entryCount == delEntry:
                                    group.remove(entry)
                                    break
                                entryCount += 1

                # if we don't have enough dudes, kill the group with the biggest point value
                elif totalDudes < minDudes and iteration != maxIterations-1:
                    biggestValue = 9999
                    biggestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] > biggestValue or biggestEntry is None:
                                biggestValue = entry[0]
                                biggestEntry = entry
                                biggestEntryGroup = group
                    if biggestEntry is not None: biggestEntryGroup.remove(biggestEntry)

                # if we've got too many dudes, kill the group with the smallest point value
                elif totalDudes > maxDudes and iteration != maxIterations-1:
                    smallestValue = 9999
                    smallestEntry = None
                    for group in groups:
                        for entry in group:
                            if entry[0] < smallestValue or smallestEntry is None:
                                smallestValue = entry[0]
                                smallestEntry = entry
                                smallestEntryGroup = group
                    smallestEntryGroup.remove(smallestEntry)

                # close enough.. we're done.
                else:
                    if diff == 0: break

        return groups


        
    def spawnPlayer(self,player):

        # we keep track of who got hurt each wave for score purposes
        player.gameData['hasBeenHurt'] = False
    
        pos = (self._spawnCenter[0]+random.uniform(-1.5,1.5),self._spawnCenter[1],self._spawnCenter[2]+random.uniform(-1.5,1.5))
        s = self.spawnPlayerSpaz(player,position=pos)
        s.impactScale = 1.00
        s.addDroppedBombCallback(self._handlePlayerDroppedBomb)

    def _handlePlayerDroppedBomb(self,player,bomb):
        self._playerHasDroppedBomb = True

    def _dropPowerup(self,index,powerupType=None):
        powerupType = bs.Powerup.getFactory().getRandomPowerupType(forceType=powerupType)
        bs.Powerup(position=self.getMap().powerupSpawnPoints[index],powerupType=powerupType).autoRetain()

    def _startPowerupDrops(self):
    	self._powerupDropTimer = bs.Timer(3000,bs.WeakCall(self._dropPowerups),repeat=True)

    def _dropPowerups(self,standardPoints=False,powerupType=None):
        """ Generic powerup drop """

        if standardPoints:
            pts = self.getMap().powerupSpawnPoints
            for i,pt in enumerate(pts):
                bs.gameTimer(1000+i*500,bs.WeakCall(self._dropPowerup,i,powerupType if i == 0 else None))
        else:
            pt = (self._powerupCenter[0]+random.uniform(-1.0*self._powerupSpread[0],1.0*self._powerupSpread[0]),
                  self._powerupCenter[1],self._powerupCenter[2]+random.uniform(-self._powerupSpread[1],self._powerupSpread[1]))

            # drop one random one somewhere..
            bs.Powerup(position=pt,powerupType=bs.Powerup.getFactory().getRandomPowerupType(excludeTypes=self._excludePowerups)).autoRetain()

    def doEnd(self,outcome,delay=0):

        if outcome == 'defeat':
            self.fadeToRed()

        if self._wave == 3:
            score = self._score
            failMessage = None
            self._awardAchievement('Derrota Monstruosa')
            
        #if self._wave == 3:
            #score = self._score
            #failMessage = None
            #self._awardAchievement('Derrota Monstruosa')
            
        if self._wave >= 4:
            score = self._score
            failMessage = None
        else:
            score = None
            failMessage = bs.Lstr(resource='FailTexto')
        self.end({'outcome':outcome,'score':score,'failMessage':failMessage,'playerInfo':self.initialPlayerInfo},delay=delay)

    def _updateWaves(self):

        # if we have no living bots, go to the next wave
        if self._canEndWave and not self._bots.haveLivingBots() and not self._gameOver:

            self._canEndWave = False

            self._timeBonusTimer = None
            self._timeBonusText = None

            won = (self._wave == len(self._waves))

            # reward time bonus
            baseDelay = 4000 if won else 0

            if self._timeBonus > 0:
                bs.gameTimer(0,lambda: bs.playSound(self._cashRegisterSound))
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardTimeBonus,self._timeBonus))
                baseDelay += 1000

            # reward flawless bonus
            if self._wave > 0:
                haveFlawless = False
                for player in self.players:
                    if player.isAlive() and player.gameData['hasBeenHurt'] == False:
                        haveFlawless = True
                        bs.gameTimer(baseDelay,bs.WeakCall(self._awardFlawlessBonus,player))
                    player.gameData['hasBeenHurt'] = False # reset
                if haveFlawless: baseDelay += 1000

            if won:
                #unlockStr = bs.Lstr(resource='somethingUnlocked',subs=[('${ITEM}',resource='characterNames.Mictlan')])
                
                self.showZoomMessage(bs.Lstr(resource='victoryText'),scale=1.0,duration=4000)
        
                self.celebrate(20000)
                self._awardAchievement('Final',sound=False)
                bs.gameTimer(baseDelay,bs.WeakCall(self._awardCompletionBonus))
                baseDelay += 1250
                bs.playSound(self._winSound)
                self.cameraFlash()
                bs.playMusic('Victory')
                self._gameOver = True

                # cant just pass delay to doEnd because our extra bonuses havnt been added yet
                # (once we call doEnd the score gets locked in)
                bs.gameTimer(baseDelay,bs.WeakCall(self.doEnd,'victory'))

                return

            self._wave += 1

            # short celebration after waves
            if self._wave > 1: self.celebrate(750)
                            
            bs.gameTimer(baseDelay,bs.WeakCall(self._startNextWave))

    def _awardCompletionBonus(self):
        bs.playSound(self._cashRegisterSound)
        for player in self.players:
            try:
                if player.isAlive():
                    self.scoreSet.playerScored(player,int(self.completionBonus/len(self.initialPlayerInfo)),scale=1.4,color=(0.6,0.6,1.0,1.0),title=bs.Lstr(resource='completionBonusText'),screenMessage=False)
            except Exception,e:
                print 'EXC in _awardCompletionBonus',e
        
    def _awardTimeBonus(self,bonus):
        bs.playSound(self._cashRegisterSound)
        bs.PopupText(bs.Lstr(value='+${A} ${B}',subs=[('${A}',str(bonus)),('${B}',bs.Lstr(resource='timeBonusText'))]),
                     color=(1,1,0.5,1),
                     scale=1.0,
                     position=(0,3,-1)).autoRetain()
        self._score += self._timeBonus
        self._updateScores()

    def _awardFlawlessBonus(self,player):
        bs.playSound(self._cashRegisterSound)
        try:
            if player.isAlive():
                self.scoreSet.playerScored(player,self._flawlessBonus,scale=1.2,color=(0.6,1.0,0.6,1.0),title=bs.Lstr(resource='flawlessWaveText'),screenMessage=False)
        except Exception,e:
            print 'EXC in _awardFlawlessBonus',e
    
    def _startTimeBonusTimer(self):
        self._timeBonusTimer = bs.Timer(1000,bs.WeakCall(self._updateTimeBonus),repeat=True)
        
    def _updatePlayerSpawnInfo(self):

        # if we have no living players lets just blank this
        if not any(player.isAlive() for player in self.teams[0].players):
            self._spawnInfoText.node.text = ''
        else:
            t = ''
            for player in self.players:
                if not player.isAlive() and (player.gameData['respawnWave'] <= len(self._waves)):
                    t = bs.Lstr(value='${A}${B}\n',subs=[('${A}',t),('${B}',bs.Lstr(resource='onslaughtRespawnText',subs=[('${PLAYER}',player.getName()),('${WAVE}',str(player.gameData['respawnWave']))]))])
            self._spawnInfoText.node.text = t

    def _startNextWave(self):

        # this could happen if we beat a wave as we die..
        # we dont wanna respawn players and whatnot if this happens
        if self._gameOver: return
        
        # respawn applicable players
        if self._wave > 1 and not self.isWaitingForContinue():
            for player in self.players:
                if not player.isAlive() and player.gameData['respawnWave'] == self._wave:
                    self.spawnPlayer(player)

        self._updatePlayerSpawnInfo()

        self.showZoomMessage(bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave))]),
                             scale=1.0,duration=1000,trail=True)
        bs.gameTimer(400,bs.Call(bs.playSound,self._newWaveSound))
        if self._wave == 4 or self._wave == 8 or self._wave == 12 or self._wave == 16:
            bs.gameTimer(400,bs.Call(bs.playSound,self._specialWaveSound))
        t = 0
        dt = 200
        botAngle = random.random()*360.0

        if self._wave == 1:
            spawnTime = 3973
            t += 500
        else:
            spawnTime = 2648
            
        if self._wave == 1:
            self._waveName = bs.Lstr(resource='nWave1')
            self._colorOuter = bs.getSharedObject('globals').vignetteOuter = (0.8,0.8,0.8)
            self._colorInner = bs.getSharedObject('globals').vignetteInner = (0.8,0.8,0.8)
        elif self._wave == 2:
            self._waveName = bs.Lstr(resource='nWave2')
        elif self._wave == 3:
            self._waveName = bs.Lstr(resource='nWave3')
            self._colorOuter = bs.getSharedObject('globals').vignetteOuter = (0,0.5,0.9)
            self._colorInner = bs.getSharedObject('globals').vignetteInner = (0.8,1.4,1.4)
        elif self._wave == 4:
            self._waveName = bs.Lstr(resource='nWave4')
            self._colorOuter = bs.getSharedObject('globals').vignetteOuter = (0.5,0,0)
            self._colorInner = bs.getSharedObject('globals').vignetteInner = (1,1,1.2)
        elif self._wave == 5:
            self._waveName = bs.Lstr(resource='nWave5')
        elif self._wave == 6:
            self._waveName = bs.Lstr(resource='nWave6')
        elif self._wave == 7:
            self._waveName = bs.Lstr(resource='nWave7')
        elif self._wave == 8:
            self._waveName = bs.Lstr(resource='nWave8')
        elif self._wave == 9:
            self._waveName = bs.Lstr(resource='nWave9')
        elif self._wave == 10:
            self._waveName = bs.Lstr(resource='nWave10')
            self._colorOuter = bs.getSharedObject('globals').vignetteOuter = (0,0.5,0.9)
            self._colorInner = bs.getSharedObject('globals').vignetteInner = (0.8,1.4,1.4)
        elif self._wave == 11:
            self._waveName = bs.Lstr(resource='nWave11')
            self._colorOuter = bs.getSharedObject('globals').vignetteOuter = (0.5,0,0)
            self._colorInner = bs.getSharedObject('globals').vignetteInner = (1,1,1.2)
        elif self._wave == 12:
            self._waveName = bs.Lstr(resource='nWave12')

        offs = 0 # debugging

        wave = self._waves[self._wave-1]


        entries = []

        try: botAngle = wave['baseAngle']
        except Exception: botAngle = 0

        entries += wave['entries']

        thisTimeBonus = 0
        thisFlawlessBonus = 0

        for info in entries:
            if info is None: continue

            botType = info['type']

            if botType == 'delay':
                spawnTime += info['duration']
                continue
            if botType is not None:
                thisTimeBonus += botType.pointsMult * 20
                thisFlawlessBonus += botType.pointsMult * 5
            # if its got a position, use that
            try: point = info['point']
            except Exception: point = None
            if point is not None:
                bs.gameTimer(t,bs.WeakCall(self.addBotAtPoint,point,botType,spawnTime))
                t += dt
            else:
                try: spacing = info['spacing']
                except Exception: spacing = 5.0
                botAngle += spacing*0.5
                if botType is not None:
                    bs.gameTimer(t,bs.WeakCall(self.addBotAtAngle,botAngle,botType,spawnTime))
                    t += dt
                botAngle += spacing*0.5
            
        # we can end the wave after all the spawning happens
        bs.gameTimer(t+spawnTime-dt+10,bs.WeakCall(self._setCanEndWave))

        # reset our time bonus
        self._timeBonus = thisTimeBonus
        self._flawlessBonus = thisFlawlessBonus
        vrMode = bs.getEnvironment()['vrMode']
        self._timeBonusText = bs.NodeActor(bs.newNode('text',
                                                      attrs={'vAttach':'top',
                                                             'hAttach':'center',
                                                             'hAlign':'center',
                                                             'vrDepth':-30,
                                                             'color':(1,1,0,1) if True else (1,1,0.5,1),
                                                             'shadow':1.0 if True else 0.5,
                                                             'flatness':1.0 if True else 0.5,
                                                             'position':(0,-80),
                                                             'scale':0.8 if True else 0.6,
                                                             'text':bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])}))
        
        bs.gameTimer(5000,bs.WeakCall(self._startTimeBonusTimer))
        self._waveText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(0,1,1,1) if True else (0.7,0.7,0.7,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(0,-40),
                                                        'scale':1.3 if True else 1.1,
                                                        'text':bs.Lstr(value='${A} ${B}',subs=[('${A}',bs.Lstr(resource='waveText')),('${B}',str(self._wave)+('/'+str(len(self._waves))))])}))
                                                        
        self._waveNameText = bs.NodeActor(bs.newNode('text',
                                                 attrs={'vAttach':'top',
                                                        'hAttach':'center',
                                                        'hAlign':'center',
                                                        'vrDepth':-10,
                                                        'color':(1,0.5,0,1) if True else (0.7,0.0,0.0,1.0),
                                                        'shadow':1.0 if True else 0.7,
                                                        'flatness':1.0 if True else 0.5,
                                                        'position':(0,-60),
                                                        'scale':1.0 if True else 0.8,
                                                        'text':self._waveName}))
                                                        

    def addBotAtPoint(self,point,spazType,spawnTime=1000):
        # dont add if the game has ended
        if self._gameOver: return
        pt = self.getMap().defs.points['botSpawn'+point]
        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)
        
    def addBotAtAngle(self,angle,spazType,spawnTime=1000):

        # dont add if the game has ended
        if self._gameOver: return

        angleRadians = angle/57.2957795
        x = math.sin(angleRadians)*1.06
        z = math.cos(angleRadians)*1.06
        pt = (x/0.125,2.3,(z/0.2)-3.7)

        self._bots.spawnBot(spazType,pos=pt,spawnTime=spawnTime)

    def _updateTimeBonus(self):
        self._timeBonus = int(self._timeBonus * 0.93)
        if self._timeBonus > 0 and self._timeBonusText is not None:
            self._timeBonusText.node.text = bs.Lstr(value='${A}: ${B}',subs=[('${A}',bs.Lstr(resource='timeBonusText')),('${B}',str(self._timeBonus))])
        else: self._timeBonusText = None

    def _startUpdatingWaves(self):
        self._waveUpdateTimer = bs.Timer(2000,bs.WeakCall(self._updateWaves),repeat=True)
        
    def _updateScores(self):
        self._scoreBoard.setTeamValue(self.teams[0],self._score,maxScore=None)

        
    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazHurtMessage):
            player = m.spaz.getPlayer()
            if player is None:
                bs.printError('FIXME: getPlayer() should no longer ever be returning None')
                return
            if not player.exists(): return
            player.gameData['hasBeenHurt'] = True
            self._aPlayerHasBeenHurt = True

        elif isinstance(m,bs.PlayerScoredMessage):
            self._score += m.score
            self._updateScores()

        elif isinstance(m,bs.PlayerSpazDeathMessage):
            self.__superHandleMessage(m) # augment standard behavior
            player = m.spaz.getPlayer()
            self._aPlayerHasBeenHurt = True
            # make note with the player when they can respawn
            if self._wave < 10: player.gameData['respawnWave'] = max(2,self._wave+1)
            elif self._wave < 15: player.gameData['respawnWave'] = max(2,self._wave+2)
            else: player.gameData['respawnWave'] = max(2,self._wave+3)
            bs.gameTimer(100,self._updatePlayerSpawnInfo)
            bs.gameTimer(100,self._checkRoundOver)

        elif isinstance(m,bs.SpazBotDeathMessage):
            pts,importance = m.badGuy.getDeathPoints(m.how)
            if m.killerPlayer is not None:
                try: target = m.badGuy.node.position
                except Exception: target = None
                try:
                    killerPlayer = m.killerPlayer
                    self.scoreSet.playerScored(killerPlayer,pts,target=target,kill=True,screenMessage=False,importance=importance)
                    bs.playSound(self._dingSound if importance == 1 else self._dingSoundHigh,volume=0.6)
                except Exception: pass
            # normally we pull scores from the score-set, but if there's no player lets be explicit..
            else: self._score += pts
            self._updateScores()
        else:
            self.__superHandleMessage(m)

    def _setCanEndWave(self):
        self._canEndWave = True

    def __superHandleMessage(self,m):
        super(FinalCSMPGameBeta,self).handleMessage(m)

    def endGame(self):
        # tell our bots to celebrate just to rub it in
        self._bots.finalCelebrate()
        
        self._gameOver = True
        self.doEnd('defeat',delay=2000)
        bs.playMusic('Defeat')

    def onContinue(self):
        for player in self.players:
            if not player.isAlive():
                self.spawnPlayer(player)
        
    def _checkRoundOver(self):
        """ see if the round is over in response to an event (player died, etc) """

        # if we already ended it doesn't matter
        if self.hasEnded(): return

        if not any(player.isAlive() for player in self.teams[0].players):
            # allow continuing after wave 1
            if self._wave > 1: self.continueOrEndGame()
            else: self.endGame()

