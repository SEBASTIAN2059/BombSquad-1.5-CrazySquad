# -*- coding: utf-8 -*-
import bs
import bsInternal
import bsPowerup
import bsUtils
import random
import settings
#import portalObjects

class chatOptions(object):
    def __init__(self):
        self.all = settings.cmd #True # just in case
       
        self.tint = None # needs for /nv
        
    def checkDevice(self,nick): # check host (settings.cmdForMe)
        n = "@"
        s = nick
        for i in bsInternal._getForegroundHostActivity().players:
            if i.getName().encode('utf-8') == nick:
                n = i.getInputDevice()._getAccountName(False)
        return bsInternal._getAccountDisplayString(False).encode('utf-8') == s
        
    def kickByNick(self,nick):
        roster = bsInternal._getGameRoster()
        for i in roster:
            try:
                if i['players'][0]['nameFull'].lower().find(nick.encode('utf-8').lower()) != -1:
                    bsInternal._disconnectClient(int(i['clientID']))
            except:
                pass
        
    def opt(self,nick,msg):
        
        gameName = bsInternal._getForegroundHostActivity().getName()
        if self.checkDevice(nick) or self.all: #and \
            #gameName != 'Final CSMP':
            m = msg.split(' ')[0] # command
            a = msg.split(' ')[1:] # arguments
            
            activity = bsInternal._getForegroundHostActivity()
            with bs.Context(activity):
                if m == '/kick':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useKick').evaluate())
                    else:
                        try:
                            if int(a[0]) != -1:
                                bsInternal._disconnectClient(int(a[0]))
                            else:
                                bsInternal._chatMessage(
                                    bs.Lstr(
                                        resource='internal.cantKickHostError'
                                        ).evaluate())
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
 ###############################              
                elif gameName == 'Final CSMP (Beta)':
                    bsInternal._chatMessage(bs.Lstr(resource='commandsDisableText').evaluate())
 ###################
                elif m in ['/list', '/l']:
                    bsInternal._chatMessage(
                        bs.Lstr(resource='forKick').evaluate()
                        )

                    for i in bsInternal._getGameRoster():
                        try:
                            bsInternal._chatMessage(
                                i['players'][0]['nameFull']+' (/kick '+str(
                                    i['clientID'])+')')
                        except:
                            pass

                    bsInternal._chatMessage(
                        '===================================')
                    bsInternal._chatMessage(
                        bs.Lstr(resource='forOtherCommands').evaluate())

                    for s in activity.players:
                        bsInternal._chatMessage(
                        	s.getName()+' - '+str(activity.players.index(s)))
                        
                elif m in ['/ooh', '/o']:
                    if a is not None and len(a) > 0:
                        s = int(a[0])

                        def oohRecurce(c):
                            bs.playSound(bs.getSound('ooh'), volume=2)
                            c -= 1
                            if c > 0:
                                time = int(a[1]) if len(a) > 1 and \
                                    a[1] is not None else 1000
                                bs.gameTimer(time, bs.Call(oohRecurce, c=c))

                        oohRecurce(c=s)
                    else:
                        bs.playSound(bs.getSound('ooh'), volume=2)

                elif m in ['/playSound', '/ps']:
                    if a is not None and len(a) > 1:
                        s = int(a[1])

                        def oohRecurce(c):
                            bs.playSound(bs.getSound(str(a[0])), volume=2)
                            c -= 1
                            if c > 0:
                                time = int(a[2]) if len(a) > 2 and \
                                    a[2] is not None else 1000
                                bs.gameTimer(time, bs.Call(oohRecurce, c=c))

                        oohRecurce(c=s)
                    else:
                        bs.playSound(bs.getSound(str(a[0])), volume=2)
                        
                elif m == '/quit':
                    bsInternal.quit()
                    
                elif m == '/nv':
                    if self.tint is None:
                        self.tint = bs.getSharedObject('globals').tint

                    if a == [] or not a[0] == u'off':
                        bs.getSharedObject('globals').tint = (0.5, 0.7, 1.0)
                    else:
                        bs.getSharedObject('globals').tint = self.tint

                elif m == '/dv':
                    if self.tint is None:
                        self.tint = bs.getSharedObject('globals').tint

                    if a == [] or not a[0] == u'off':
                        bs.getSharedObject('globals').tint = (1.0, 1.0, 1.0)
                    else:
                        bs.getSharedObject('globals').tint = self.tint
                        
                elif m == '/freeze':
                    if a == []:
                        bsInternal._chatMessage(bs.Lstr(resource='useFreeze').evaluate())
                    else:
                        if a[0] == 'all':
                            for i in bs.getSession().players:
                                try:
                                    i.actor.node.handleMessage(bs.FreezeMessage())
                                except:
                                    pass
                        else:
                            bs.getSession().players[int(a[0])].actor.node.handleMessage(bs.FreezeMessage())
                            
                elif m == '/thaw':
                    if a == []:
                        bsInternal._chatMessage(bs.Lstr(resource='useThaw').evaluate())
                    else:
                        if a[0] == 'all':
                            for i in bs.getSession().players:
                                try:
                                    i.actor.node.handleMessage(bs.ThawMessage())
                                except:
                                    pass
                        else:
                            bs.getSession().players[int(a[0])].actor.node.handleMessage(bs.ThawMessage())
                            
                elif m == '/kill':
                    if a == []:
                        bsInternal._chatMessage(bs.Lstr(resource='useKill').evaluate())
                    else:
                        if a[0] == 'all':
                            for i in bs.getSession().players:
                                try:
                                    i.actor.node.handleMessage(bs.DieMessage())
                                except:
                                    pass
                        else:
                            bs.getSession().players[int(a[0])].actor.node.handleMessage(bs.DieMessage())
                            
                elif m == '/curse':
                    if a == []:
                        bsInternal._chatMessage(bs.Lstr(resource='useCurse').evaluate())
                    else:
                        if a[0] == 'all':
                            for i in bs.getSession().players:
                                try:
                                    i.actor.curse()
                                except:
                                    pass
                        else:
                            bs.getSession().players[int(a[0])].actor.curse()
                            
                elif m == '/box':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBox').evaluate())

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.torsoModel = \
                                    bs.getModel('tnt')
                                i.actor.node.colorMaskTexture = \
                                    bs.getTexture('tnt')
                                i.actor.node.colorTexture = \
                                    bs.getTexture('tnt')
                                i.actor.node.highlight = (1, 1, 1)
                                i.actor.node.color = (1, 1, 1)
                                i.actor.node.headModel = None
                                i.actor.node.style = 'cyborg'
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(
                                    False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.torsoModel = \
                                        bs.getModel('tnt')
                                    i.actor.node.colorMaskTexture = \
                                        bs.getTexture('tnt')
                                    i.actor.node.colorTexture = \
                                        bs.getTexture('tnt')
                                    i.actor.node.highlight = (1, 1, 1)
                                    i.actor.node.color = (1, 1, 1)
                                    i.actor.node.headModel = None
                                    i.actor.node.style = 'cyborg'
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate(
                                        ))

                    else:
                        try:
                            i = activity.players[int(a[0])].actor.node
                            i.torsoModel = bs.getModel('tnt')
                            i.colorMaskTexture = bs.getTexture('tnt')
                            i.colorTexture = bs.getTexture('tnt')
                            i.highlight = (1, 1, 1)
                            i.color = (1, 1, 1)
                            i.headModel = None
                            i.style = 'cyborg'
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
                           
                elif m == '/remove':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useRemove').evaluate())

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.removeFromGame()
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(
                                    False).encode('utf-8') == a[1]:
                                try:
                                    i.removeFromGame()
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate(
                                        ))

                    else:
                        try:
                            activity.players[int(a[0])].removeFromGame()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
                            
                elif m == '/end':
                    try:
                        bsInternal._getForegroundHostActivity().endGame()
                    except:
                        pass
                        
                elif m == '/hug':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useHug').evaluate())

                    elif a[0] == 'all':
                        try:
                            activity.players[0].actor.node.holdNode = \
                                activity.players[1].actor.node
                        except:
                            pass

                        try:
                            activity.players[1].actor.node.holdNode = \
                                activity.players[0].actor.node
                        except:
                            pass

                        try:
                            activity.players[2].actor.node.holdNode = \
                                activity.players[3].actor.node
                        except:
                            pass

                        try:
                            activity.players[3].actor.node.holdNode = \
                                activity.players[2].actor.node
                        except:
                            pass

                        try:
                            activity.players[4].actor.node.holdNode = \
                                activity.players[5].actor.node
                        except:
                            pass

                        try:
                            activity.players[5].actor.node.holdNode = \
                                activity.players[4].actor.node
                        except:
                            pass

                        try:
                            activity.players[6].actor.node.holdNode = \
                                activity.players[7].actor.node
                        except:
                            pass

                        try:
                            activity.players[7].actor.node.holdNode = \
                                activity.players[6].actor.node
                        except:
                            pass

                    else:
                        activity.players[int(a[0])].actor.node.holdNode = \
                            activity.players[int(a[1])].actor.node
                           
                elif m == '/gm':
                    #if not admin and settings.cmdNew:
                        #return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useGM').evaluate())

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                if not i.actor.node.hockey:
                                    i.actor.node.hockey = True
                                else:
                                    i.actor.node.hockey = False

                                if not i.actor.node.invincible:
                                    i.actor.node.invincible = True
                                else:
                                    i.actor.node.invincible = False

                                if i.actor._punchPowerScale == 1.2:
                                    i.actor._punchPowerScale = 5
                                else:
                                    i.actor._punchPowerScale = 1.2
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(
                                    False).encode('utf-8') == a[1]:
                                try:
                                    if not i.actor.node.hockey:
                                        i.actor.node.hockey = True
                                    else:
                                        i.actor.node.hockey = False

                                    if not i.actor.node.invincible:
                                        i.actor.node.invincible = True
                                    else:
                                        i.actor.node.invincible = False

                                    if i.actor._punchPowerScale == 1.2:
                                        i.actor._punchPowerScale = 5
                                    else:
                                        i.actor._punchPowerScale = 1.2
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate(
                                        ))

                    else:
                        try:
                            if not activity.players[
                                    int(a[0])].actor.node.hockey:
                                activity.players[
                                    int(a[0])].actor.node.hockey = True
                            else:
                                activity.players[
                                    int(a[0])].actor.node.hockey = False

                            if not activity.players[
                                    int(a[0])].actor.node.invincible:
                                activity.players[
                                    int(a[0])].actor.node.invincible = True
                            else:
                                activity.players[
                                    int(a[0])].actor.node.invincible = False

                            if not activity.players[
                                    int(a[0])].actor._punchPowerScale == 1.2:
                                activity.players[
                                    int(a[0])].actor._punchPowerScale = 5
                            else:
                                activity.players[
                                    int(a[0])].actor._punchPowerScale = 1.2
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
                        
                elif m == '/tint':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useTint').evaluate())
                    else:
                        if a[0] == 'r':
                            m = 1.3 if a[1] is None else float(a[1])
                            s = 1000 if a[2] is None else float(a[2])
                            values = {
                                0: (1*m, 0, 0), s: (0, 1*m, 0),
                                s*2: (0, 0, 1*m), s*3: (1*m, 0, 0)
                            }

                            bs.animateArray(
                                bs.getSharedObject('globals'), 'tint', 3,
                                values, True)
                        else:
                            try:
                                bs.getSharedObject('globals').tint = (
                                    float(a[0]), float(a[1]), float(a[2]))
                            except:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='errorText').evaluate())
                                
                elif m == '/pause':
                    if not bs.getSharedObject('globals').paused:
                        bs.getSharedObject('globals').paused = True
                    else:
                        bs.getSharedObject('globals').paused = False
                    
                elif m == '/sm':
                    if not bs.getSharedObject('globals').slowMotion:
                        bs.getSharedObject('globals').slowMotion = True
                    else:
                        bs.getSharedObject('globals').slowMotion = False
                    
                elif m == '/bot':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBot').evaluate()
                            )
                    else:
                        for i in xrange(int(a[0])):
                            p = bs.getSession().players[int(a[1])]
                            if 'bunnies' not in p.gameData:
                                p.gameData['bunnies'] = BuddyBunny.BunnyBotSet(
                                    p)

                            p.gameData['bunnies'].doBunny()
                        
                elif m in ['/cameraMode', '/cam']:
                    try:
                        if bs.getSharedObject(
                                'globals').cameraMode == 'follow':
                            bs.getSharedObject('globals').cameraMode = 'rotate'
                        else:
                            bs.getSharedObject('globals').cameraMode = 'follow'
                    except:
                        pass
                        
                elif m == '/lm':
                    arr = []
                    for i in xrange(100):
                        try:
                            arr.append(bsInternal._getChatMessages()[-1-i])
                        except:
                            pass

                    arr.reverse()
                    for i in arr:
                        bsInternal._chatMessage(i)
                        
                elif m == '/gp':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useGP').evaluate())
                    else:
                        s = bsInternal._getForegroundHostSession()
                        for i in s.players[int(a[0])].getInputDevice(
                                )._getPlayerProfiles():
                            try:
                                if i.encode('utf-8') == '__account__':
                                    i = s.players[int(a[0])].getInputDevice(
                                        )._getAccountName(False)

                                bsInternal._chatMessage(i)
                            except:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='errorText').evaluate())
                                    
                elif m == '/icy':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useIcy').evaluate())

                    elif len(a) == 2:
                        try:
                            activity.players[int(a[0])].actor.node = \
                                activity.players[int(a[1])].actor.node

                            activity.players[int(a[1])].actor.node = \
                                activity.players[int(a[0])].actor.node
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useIcy').evaluate())
                            
                elif m == '/fly':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useFly').evaluate())

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.fly = True
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(
                                    False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.fly = True
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate(
                                        ))

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.fly = True
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
                                
                elif m == '/floorReflection':
                    bs.getSharedObject('globals').floorReflection = bs.getSharedObject('globals').floorReflection == False
                elif m == '/ac':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useAC').evaluate())
                    else:
                        if a[0] == 'r':
                            m = 1.3 if a[1] is None else float(a[1])
                            s = 1000 if a[2] is None else float(a[2])
                            values = {
                                0: (1*m, 0, 0), s: (0, 1*m, 0),
                                s*2: (0, 0, 1*m), s*3: (1*m, 0, 0)
                            }

                            bs.animateArray(
                                bs.getSharedObject('globals'), 'ambientColor',
                                3, values, True)
                        else:
                            try:
                                bs.getSharedObject('globals').ambientColor = (
                                    float(a[0]), float(a[1]), float(a[2]))
                            except:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='errorText').evaluate()
                                    )
                                    
                elif m == '/iceOff':
                    try:
                        activity.getMap().node.materials = [bs.getSharedObject('footingMaterial')]
                        activity.getMap().isHockey = False
                    except:
                        pass
                    try:
                        activity.getMap().floor.materials = [bs.getSharedObject('footingMaterial')]
                        activity.getMap().isHockey = False
                    except:
                        pass
                    for i in activity.players:
                        i.actor.node.hockey = False
                        
                elif m in ['/maxPlayers', '/mp']:
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useMP').evaluate())
                    else:
                        try:
                            bsInternal._getForegroundHostSession(
                                )._maxPlayers = int(a[0])
                            bsInternal._setPublicPartyMaxSize(int(a[0]))
                            bsInternal._chatMessage(
                                bs.Lstr(resource='limitPlayer').evaluate()+str(int(a[0])))
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
                                
                elif m == '/heal':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useHeal').evaluate())

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(
                                    False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.handleMessage(
                                        bs.PowerupMessage(
                                            powerupType='health'))
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(
                                            resource='errorText').evaluate())

                    else:
                        try:
                            activity.players[
                                int(a[0])].actor.node.handleMessage(
                                    bs.PowerupMessage(powerupType='health'))
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
                                 
                elif m in ['/reflections', '/ref']:
                    if a == [] or len(a) < 2:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useRef').evaluate())

                    rs = [int(a[1])]
                    type = 'soft' if int(a[0]) == 0 else 'powerup'
                    try:
                        activity.getMap().node.reflection = type
                        activity.getMap().node.reflectionScale = rs
                    except:
                        pass

                    try:
                        activity.getMap().bg.reflection = type
                        activity.getMap().bg.reflectionScale = rs
                    except:
                        pass

                    try:
                        activity.getMap().floor.reflection = type
                        activity.getMap().floor.reflectionScale = rs
                    except:
                        pass

                    try:
                        activity.getMap().center.reflection = type
                        activity.getMap().center.reflectionScale = rs
                    except:
                        pass
                        
                elif m == '/shatter':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useShatter').evaluate())

                    elif a[0] == 'all':
                        for i in activity.players:
                            i.actor.node.shattered = 1
                            
                    elif a[0] == 'off':
                        for i in activity.players:
                            i.actor.node.shattered = 0
                            
                    else:
                        activity.players[
                            int(a[0])].actor.node.shattered = 1
                            
                elif m == '/cm':
                    if a == []:
                        time = 8000
                    else:
                        time = int(a[0])
                        
                        op = 0.08
                        std = bs.getSharedObject('globals').vignetteOuter
                        bsUtils.animateArray(bs.getSharedObject('globals'),'vignetteOuter',3,{0:bs.getSharedObject('globals').vignetteOuter,17000:(0,1,0)})
                        
                    try:
                        bsInternal._getForegroundHostActivity().getMap().node.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().bg.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().bg.node.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().node1.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().node2.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().node3.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().steps.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().floor.opacity = op
                    except:
                        pass
                    try:
                        bsInternal._getForegroundHostActivity().getMap().center.opacity = op
                    except:
                        pass
                        
                    def off():
                        op = 1
                        try:
                            bsInternal._getForegroundHostActivity().getMap().node.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().bg.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().bg.node.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().node1.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().node2.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().node3.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().steps.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().floor.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap().center.opacity = op
                        except:
                            pass
                        bsUtils.animateArray(bs.getSharedObject('globals'),'vignetteOuter',3,{0:bs.getSharedObject('globals').vignetteOuter,100:std})
                    bs.gameTimer(time,bs.Call(off))
                    
                elif m == '/tnt':
                    #if not admin and settings.cmdNew:
                        #return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useTNT').evaluate())

                    elif a[2] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Bomb(
                                        bombType='tnt',
                                        position=pos).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    elif len(a) == 3:
                        try:
                            bs.Bomb(
                                bombType='tnt',
                                position=(float(a[0]),
                                          float(a[1]),
                                          float(a[2]))).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useTNT').evaluate())
                            
                elif m == '/bomb':
                    #if not admin and settings.cmdNew:
                        #return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBomb').evaluate())

                    elif a[0] == 'names':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='bombNames').evaluate()+":")

                        for i in xrange(1, 13):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='bombName'+str(i)).evaluate())

                        bsInternal._chatMessage(
                            '===================================')

                    elif a[2] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Bomb(
                                        bombType=str(a[0]),
                                        blastRadius=float(a[1]),
                                        position=pos).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    elif len(a) == 5:
                        try:
                            bs.Bomb(
                                bombType=str(a[0]),
                                blastRadius=float(a[1]),
                                position=(float(a[2]),
                                          float(a[3]),
                                          float(a[4]))).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBomb').evaluate())
                            
                elif m == '/blast':
                    #if not admin and settings.cmdNew:
                        #return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBlast').evaluate())

                    elif a[1] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Blast(
                                        blastRadius=float(a[0]),
                                        position=pos).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    elif len(a) == 4:
                        try:
                            bs.Blast(
                                blastRadius=float(a[0]),
                                position=(float(a[1]),
                                          float(a[2]),
                                          float(a[3]))).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBlast').evaluate())
                            
                elif m == '/powerup':
                    #if not admin and settings.cmdNew:
                        #return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='usePowerup').evaluate())

                    elif a[0] == 'names':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='powerupNames').evaluate()+':')

                        for i in xrange(1, 23):
                            bsInternal._chatMessage(
                                bs.Lstr(
                                    resource='powerupName'+str(i)).evaluate())

                        bsInternal._chatMessage(
                            '===================================')

                    elif a[1] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Powerup(
                                        powerupType=str(a[0]),
                                        position=pos).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    elif len(a) == 4:
                        try:
                            bs.Powerup(
                                powerupType=str(a[0]),
                                position=(float(a[1]),
                                          float(a[2]),
                                          float(a[3]))).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='usePowerup').evaluate())
                            
                elif m == '/rainbow':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useRainbow').evaluate())

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                colors = {
                                    0: (0, 0, 3), 500: (0, 3, 0),
                                    1000: (3, 0, 0), 1500: (0, 0, 3)
                                }
                                highlights = {
                                    0: (3, 0, 0), 500: (0, 0, 0),
                                    1000: (0, 0, 3), 1500: (3, 0, 0)
                                }

                                bs.animateArray(
                                    i.actor.node, 'color', 3,
                                    colors, True)

                                bs.animateArray(
                                    i.actor.node, 'highlight', 3,
                                    highlights, True)

                                i.actor.node.handleMessage(
                                    'celebrate', 100000000)
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(
                                    False).encode('utf-8') == a[1]:
                                try:
                                    colors = {
                                        0: (0, 0, 3), 500: (0, 3, 0),
                                        1000: (3, 0, 0), 1500: (0, 0, 3)
                                    }
                                    highlights = {
                                        0: (3, 0, 0), 500: (0, 0, 0),
                                        1000: (0, 0, 3), 1500: (3, 0, 0)
                                    }

                                    bs.animateArray(
                                        i.actor.node, 'color', 3,
                                        colors, True)

                                    bs.animateArray(
                                        i.actor.node, 'highlight', 3,
                                        highlights, True)

                                    i.actor.node.handleMessage(
                                        'celebrate', 100000000)
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate(
                                        ))

                    else:
                        try:
                            colors = {
                                0: (0, 0, 3), 500: (0, 3, 0),
                                1000: (3, 0, 0), 1500: (0, 0, 3)
                            }
                            highlights = {
                                0: (3, 0, 0), 500: (0, 0, 0),
                                1000: (0, 0, 3), 1500: (3, 0, 0)
                            }

                            bs.animateArray(
                                activity.players[int(a[0])].actor.node,
                                'color', 3, colors, True)

                            bs.animateArray(
                                activity.players[int(a[0])].actor.node,
                                'highlight', 3, highlights, True)

                            activity.players[
                                int(a[0])].actor.node.handleMessage(
                                    'celebrate', 100000000)
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate())
                                                            
                elif m == '/nameBombs':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='bombTypes').evaluate())

                        for i in xrange(1, 15):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='bomb'+str(i)).evaluate())

                        bsInternal._chatMessage(
                            '=====================================')
                    bsInternal._chatMessage(
                        bs.Lstr(resource='forOtherCommands').evaluate())
                        
                elif m == '/help':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useHelp').evaluate())

                    elif a[0] == '1':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='helpPage1').evaluate())

                        for i in xrange(1, 15):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='help'+str(i)).evaluate())

                        bsInternal._chatMessage(
                            '=====================================')

                    elif a[0] == '2':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='helpPage2').evaluate()
                            )

                        for i in xrange(15, 29):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='help'+str(i)).evaluate()
                                )

                        bsInternal._chatMessage(
                            '=====================================')

                    elif a[0] == '3':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='helpPage3').evaluate()
                            )

                        for i in xrange(29, 48):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='help'+str(i)).evaluate()
								)

                        bsInternal._chatMessage(
                            '=====================================')

        elif gameName == 'Final CSMP':
            bs.screenMessage(
                bs.Lstr(resource='notnow'),
                (1, 0.7, 0))
            
c = chatOptions()

def cmd(msg):
    if bsInternal._getForegroundHostActivity() is not None:
	#bsInternal._chatMessage("==========Comando ejecutado==========")
	bsInternal._getChatMessages()
        n = msg.split(': ')
        c.opt(n[0],n[1])
        
bs.realTimer(2000,bs.Call(bsInternal._setPartyIconAlwaysVisible,True))
