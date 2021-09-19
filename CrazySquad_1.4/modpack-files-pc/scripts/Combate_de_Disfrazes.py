#Made by Froshlee14
import random
import bs
import bsUtils
from bsSpaz import _BombDiedMessage

class PlayerSpaz_cDisf(bs.PlayerSpaz):

	def handleMessage(self, m):
		if isinstance(m, _BombDiedMessage):
			#bs.screenMessage('recyceling')
			self.bombCount += 1
		else:
			super(self.__class__, self).handleMessage(m)

	def dropBomb(self):
		if (self.bombCount <= 0) or self.frozen:
			return
		p = self.node.positionForward
		v = self.node.velocity         

        #Bombas random para mayor diversion!
		bombType = random.choice(['normal','ice','impact','sticky','landMine','tnt','luckyBomb'])

		bomb = bs.Bomb(position=(p[0], p[1] - 0.0, p[2]),
					   velocity=(v[0], v[1], v[2]),
					   bombType=bombType,
					   blastRadius=self.blastRadius,
					   sourcePlayer=self.sourcePlayer,
					   owner=self.node).autoRetain()

		bsUtils.animate(bomb.node, 'modelScale', {0:1.0,
								   250:0.9,
								   250:1.0},loop = True)

		self.bombCount -= 1
		bomb.node.addDeathAction(bs.WeakCall(self.handleMessage, _BombDiedMessage()))

		self._pickUp(bomb.node)

		for meth in self._droppedBombCallbacks:
			meth(self, bomb)

		return bomb


def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [DeathMatchGame]

class DeathMatchGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Combate de Disfrazes'

    @classmethod
    def getDescription(cls,sessionType):
        return ('Quien Soy Yo?\nPor que tengo este cuerpo y este nombre?\nPOR QUE NADIE DICE NADA!!!?')

    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return bs.getMapsSupportingPlayType("melee")

    @classmethod
    def getSettings(cls,sessionType):
        return [("Matar Disfrazados para ganar",{'minValue':1,'default':5,'increment':1}),
                 ("Max Bombs", {'minValue':1,'maxValue':20,'default':1,'increment':1}),
                ("Time Limit",{'choices':[('None',0),('1 Minute',60),
                                        ('2 Minutes',120),('5 Minutes',300),
                                        ('10 Minutes',600),('20 Minutes',1200)],'default':0}),
                ("Respawn Times",{'choices':[('Shorter',0.25),('Short',0.5),('Normal',1.0),('Long',2.0),('Longer',4.0)],'default':1.0}),
                ("Epic Mode",{'default':False})]


    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        if self.settings['Epic Mode']: self._isSlowMotion = True
        self.info = bs.NodeActor(bs.newNode('text',
                                                   attrs={'vAttach': 'bottom',
                                                          'hAlign': 'center',
                                                          'vrDepth': 0,
                                                          'color': (0,0.8,0.7),
                                                          'shadow': 1.0,
                                                          'flatness': 1.0,
                                                          'position': (0,0),
                                                          'scale': 1.0,
                                                          'text': "Created by SEBASTIAN2059",
                                                          }))
        # print messages when players die since it matters here..
        self.announcePlayerDeaths = True
        
        self._scoreBoard = bs.ScoreBoard()

    def getInstanceDescription(self):
        return ('Mata ${ARG1} enemigos disfrazados.',self._scoreToWin)

    def getInstanceScoreBoardDescription(self):
        return ('Mata ${ARG1} enemigos disfrazados',self._scoreToWin)

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'GrandRomp')

        #Let's do it more funny! (and extreme)
        if self.settings:
            bs.getSharedObject('globals').tint=(0.8,0.6,0.5)
            bs.getSharedObject('globals').vignetteOuter = (0.7,0.7,0.7)

    def onTeamJoin(self,team):
        team.gameData['score'] = 0
        if self.hasBegun(): self._updateScoreBoard()

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.setupStandardTimeLimit(self.settings['Time Limit'])
        if len(self.teams) > 0:
            self._scoreToWin = self.settings['Matar Disfrazados para ganar'] * max(1,max(len(t.players) for t in self.teams))
        else: self._scoreToWin = self.settings['Matar Disfrazados para ganar']
        self._updateScoreBoard()
        self._dingSound = bs.getSound('dingSmall')

    def spawnPlayer(self, player):
		if isinstance(self.getSession(), bs.TeamsSession):
			position = self.getMap().getStartPosition(player.getTeam().getID())
		else:
			# otherwise do free-for-all spawn locations
			position = self.getMap().getFFAStartPosition(self.players)

		angle = None
		name = player.getName()

		lightColor = bsUtils.getNormalizedColor(player.color)
		displayColor = bs.getSafeColor(player.color, targetIntensity=0.75)

		spaz = PlayerSpaz_cDisf(color=(random.random()*4,random.random()*4,random.random()*4),
							 highlight=(random.random()*5,random.random()*5,random.random()*5),
							 character=random.choice(['Bernard','Easter Bunny','Zoe','Kronk','Grumbledorf','B-9000','Taobao Mascot','Bones','Santa Claus','Jack Morgan','Mel','Frosty','Snake Shadow','Pixel','Pascal','Agent Johnson']),
							 player=player)
		player.setActor(spaz)

		if isinstance(self.getSession(), bs.CoopSession) and self.getMap().getName() in ['Courtyard', 'Tower D']:
			mat = self.getMap().preloadData['collideWithWallMaterial']

			spaz.node.materials += (mat,)
			spaz.node.rollerMaterials += (mat,)

		spaz.node.name = random.choice(['Loko','Lol','CRAZY','Noob','Soy Yo','QUIEN SOY YO?','01011011','WTF!!','NN','El Asesino','El GAY','1+1=2?','Hola mundo','QUIERO MATAR!!!','No se Jugar','Soy Amigo Tuyo','Un Amigo'])
		spaz.node.nameColor = displayColor
		spaz.connectControlsToPlayer(enablePunch=True)
		self.scoreSet.playerGotNewSpaz(player, spaz)
		spaz.setBombCount(self.settings['Max Bombs'])

		spaz.handleMessage(bs.StandMessage(position, angle if angle is not None else random.uniform(0, 360)))
		t = bs.getGameTime()
		bs.playSound(self._spawnSound, 1, position=spaz.node.position)
		light = bs.newNode('light', attrs={'color':(random.random()*2,random.random()*2,random.random()*2)})
		spaz.node.connectAttr('position', light, 'position')
		bsUtils.animate(light, 'radius', {7000:0.1, 3500:0, 50:0.1, 100:0,},loop =True)
		bs.gameTimer(500000, light.delete)

    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m) # augment standard behavior

            player = m.spaz.getPlayer()
            self.respawnPlayer(player)

            killer = m.killerPlayer
            if killer is None: return

            # handle team-kills
            if killer.getTeam() is player.getTeam():

                # in free-for-all, killing yourself loses you a point
                if isinstance(self.getSession(),bs.FreeForAllSession):
                    player.getTeam().gameData['score'] = max(0,player.getTeam().gameData['score']-1)

                # in teams-mode it gives a point to the other team
                else:
                    bs.playSound(self._dingSound)
                    for team in self.teams:
                        if team is not killer.getTeam():
                            team.gameData['score'] += 1

            # killing someone on another team nets a kill
            else:
                killer.getTeam().gameData['score'] += 1
                bs.playSound(self._dingSound)
                # in FFA show our score since its hard to find on the scoreboard
                try: killer.actor.setScoreText(str(killer.getTeam().gameData['score'])+'/'+str(self._scoreToWin),color=killer.getTeam().color,flash=True)
                except Exception: pass

            self._updateScoreBoard()

            # if someone has won, set a timer to end shortly
            # (allows the dust to clear and draws to occur if deaths are close enough)
            if any(team.gameData['score'] >= self._scoreToWin for team in self.teams):
                bs.gameTimer(500,self.endGame)

        else: bs.TeamGameActivity.handleMessage(self,m)

    def _updateScoreBoard(self):
        for team in self.teams:
            self._scoreBoard.setTeamValue(team,team.gameData['score'],self._scoreToWin)

    def endGame(self):
        results = bs.TeamGameResults()
        for t in self.teams: results.setTeamScore(t,t.gameData['score'])
        self.end(results=results)
