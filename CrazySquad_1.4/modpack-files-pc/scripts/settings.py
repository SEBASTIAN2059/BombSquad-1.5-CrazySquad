event = 'event_4'
menuTex = 1
menuEvent = 0
tintColor = 'Auto'
titleScale = 0
cmd = True
slowMotion = False
cameraMode = 0
map = 0
powerup_Shield = 0
night = False
button = 0
charactersWithPowers = True
character = False
forcedUI = 2
theme = 'themeCSMP'


def saveSettings():
    import bs
    with open(bs.getEnvironment()[
            'systemScriptsDirectory']+'/settings.py') as file:
        s = [row for row in file]
        s[0] = 'event = ' + "'" + str(event) + "'" + '\n'
        s[1] = 'menuTex = ' + str(menuTex) + '\n'
        s[2] = 'menuEvent = ' + str(menuEvent) + '\n'
        s[3] = 'tintColor = ' + "'" + str(tintColor) + "'" + '\n'
        s[4] = 'titleScale = ' + str(titleScale) + '\n'
        s[5] = 'cmd = ' + str(cmd) + '\n'
        s[6] = 'slowMotion = ' + str(slowMotion) + '\n'
        s[7] = 'cameraMode = ' + str(cameraMode) + '\n'
        s[8] = 'map = ' + str(map) + '\n'
        s[9] = 'powerup_Shield = ' + str(powerup_Shield) + '\n'
        s[10] = 'night = ' + str(night) + '\n'
        s[11] = 'button = ' + str(button) + '\n'
        s[12] = 'charactersWithPowers = ' + str(charactersWithPowers) + '\n'
        s[13] = 'character = ' + str(character) + '\n'
        s[14] = 'forcedUI = ' + str(forcedUI) + '\n'
        s[15] = 'theme = ' + "'" + str(theme) + "'" + '\n'

    f = open(
        bs.getEnvironment()['systemScriptsDirectory']+'/settings.py', 'w')

    for i in s:
        f.write(i)

    f.close()
    