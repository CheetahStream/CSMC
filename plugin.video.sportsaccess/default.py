import urllib,urllib2,re,cookielib,string,os,random
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from t0mm0.common.net import Net as net

addon_id = 'plugin.video.sportsaccess'
AddonID = "plugin.video.sportsaccess"
artpath = xbmc.translatePath(os.path.join('special://home/addons/' + AddonID + '/resources/'))
ADDON=xbmcaddon.Addon(id='plugin.video.sportsaccess')
selfAddon = xbmcaddon.Addon(id=addon_id)
prettyName='SportsAccess'
fanart= xbmc.translatePath(os.path.join('special://home/addons/' + AddonID , 'fanart.jpg'))
icon= xbmc.translatePath(os.path.join('special://home/addons/' + AddonID , 'icon.jpg'))
art = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.sportsaccess/resources/art', ''))
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
UpdatePath=os.path.join(datapath,'Update')
cookiedir = os.path.join(os.path.join(datapath,'Cookies'))
cookie_file = os.path.join(os.path.join(datapath,'Cookies'), 'sportsaccess.cookies')

try: os.makedirs(UpdatePath)
except: pass

try: os.makedirs(cookiedir)
except: pass

if selfAddon.getSetting("server-location") == "true":
    BASE_URL = 'usplayer'
else:
    BASE_URL = 'euplayer'

def OPENURL(url, mobile = False, q = False, verbose = True, timeout = 10, cookie = None, data = None,
            cookiejar = False, log = True, headers = [], type = '',ua = False,setCookie = [],raiseErrors = False,ignore_discard = True):
    import urllib2 
    UserAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    if ua: UserAgent = ua
    try:
        if log:
            print "MU-Openurl = " + url
        if cookie and not cookiejar:
            import cookielib
            cookie_file = os.path.join(os.path.join(datapath,'Cookies'), cookie+'.cookies')
            cj = cookielib.LWPCookieJar()
            if os.path.exists(cookie_file):
                try:
                    cj.load(cookie_file,ignore_discard)
                    for c in setCookie:
                        cj.set_cookie(c)
                except: cj.save(cookie_file,True)
            else: cj.save(cookie_file,True)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        elif cookiejar:
            import cookielib
            cj = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
            opener = urllib2.build_opener()
        if mobile:
            opener.addheaders = [('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')]
        else:
            opener.addheaders = [('User-Agent', UserAgent)]
        for header in headers:
            opener.addheaders.append(header)
        if data:
            if type == 'json': 
                import json
                data = json.dumps(data)
                opener.addheaders.append(('Content-Type', 'application/json'))
            else: data = urllib.urlencode(data)
        response = opener.open(url, data, timeout)
        if cookie and not cookiejar:
            cj.save(cookie_file,ignore_discard)
        opener.close()
        link=response.read()
        response.close()
        #link = net(UserAgent).http_GET(url).content
        link=link.replace('&#39;',"'").replace('&quot;','"').replace('&amp;',"&").replace("&#39;","'").replace('&lt;i&gt;','').replace("#8211;","-").replace('&lt;/i&gt;','').replace("&#8217;","'").replace('&amp;quot;','"').replace('&#215;','x').replace('&#038;','&').replace('&#8216;','').replace('&#8211;','').replace('&#8220;','').replace('&#8221;','').replace('&#8212;','')
        link=link.replace('%3A',':').replace('%2F','/')
        if q: q.put(link)
        return link
    except Exception as e:
        if raiseErrors: raise
        if verbose:
            from urlparse import urlparse
            host = urlparse(url).hostname.replace('www.','').partition('.')[0]
            xbmc.executebuiltin("XBMC.Notification(Sorry!,"+host.title()+" Website is Down,3000,"+icon+")")
        xbmc.log('***********Website Error: '+str(e)+'**************', xbmc.LOGERROR)
        xbmc.log('***********Url: '+url+' **************', xbmc.LOGERROR)
        import traceback
        traceback.print_exc()
        link ='website down'
        if q: q.put(link)
        return link


def setFile(path,content,force=False):
    if os.path.exists(path) and not force:
        return False
    else:
        try:
            open(path,'w+').write(content)
            return True
        except: pass
    return False

user = selfAddon.getSetting('skyusername')
passw = selfAddon.getSetting('skypassword')
if user == '' or passw == '':
    if os.path.exists(cookie_file):
        try: os.remove(cookie_file)
        except: pass
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('[COLOR red]SportsAccess[/COLOR]', 'Please set your SportsAccess credentials','or register if you don have an account','at sportsaccess.se','Cancel','Login')
    if ret == 1:
        keyb = xbmc.Keyboard('', 'Enter Username or Email')
        keyb.doModal()
        if (keyb.isConfirmed()):
            search = keyb.getText()
            username=search
            keyb = xbmc.Keyboard('', 'Enter Password:')
            keyb.doModal()
            if (keyb.isConfirmed()):
                search = keyb.getText()
                password=search
                selfAddon.setSetting('skyusername',username)
                selfAddon.setSetting('skypassword',password)
                
user = selfAddon.getSetting('skyusername')
passw = selfAddon.getSetting('skypassword')

"""def setCookie(srDomain):
        html = net().http_GET(srDomain).content
        r = re.findall(r'<input name="(.+?)" value="(.+?)" type="hidden">', html, re.I)
        post_data = {}
        post_data['vb_login_username'] = user
        post_data['vb_login_password'] = passw
        import hashlib
        m = hashlib.md5()
        m.update(passw)
        md5= m.hexdigest()
        post_data['vb_login_md5password'] = md5
        post_data['vb_login_md5password_utf'] = md5
        for name, value in r:
            post_data[name] = value
        net().http_GET('http://sportsaccess.se/login.php?do=login')
        net().http_POST('http://sportsaccess.se/login.php?do=login',post_data)"""

def setCookie():
    cookieExpired = False
    if os.path.exists(cookie_file):
        try:
            import time,datetime
            cookie = open(cookie_file).read()
            matches = re.finditer('(?i)expires="(.*?)"',cookie)
            for expire in matches:
                if expire:
                    expire = str(expire.group(1))
                    if time.time() > time.mktime(time.strptime(expire, '%Y-%m-%d %H:%M:%SZ')):
                       cookieExpired = True
            if time.mktime(datetime.date.yesterday().timetuple()) > os.stat(cookie_file).st_mtime:
               cookieExpired = True
        except: cookieExpired = True 
    if not os.path.exists(cookie_file) or cookieExpired or (not loggedin and user != '' and passw != '') or not apifile:
        data = {}
        data['vb_login_username'] = user
        data['vb_login_password'] = passw

        import hashlib
        m = hashlib.md5()
        m.update(passw)
        md5= m.hexdigest()
        data['vb_login_md5password'] = md5
        data['vb_login_md5password_utf'] = md5
        data['s'] = ''
        data['do'] = 'login'
        OPENURL('http://sportsaccess.se/login.php?do=login',data=data,cookie='sportsaccess')


           
def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))

def MAINSA():
    setCookie()
    link  = OPENURL('http://sportsaccess.se/index.php?pg=schedule',cookie='sportsaccess')
    link2 = OPENURL('http://sportsaccess.se/index.php?pg=usa',cookie='sportsaccess')
    link = cleanHex(link)
    link2 = cleanHex(link2)
    #print link
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    if '<li><a title="Log Out"' in link2:
        if selfAddon.getSetting("server-location") == "true":
            addLink2('[COLOR red]Select Server Location[/COLOR]: USA','f',240,art+'/51-Star-Flag.png',fanart)
        else:
            addLink2('[COLOR red]Select Server Location[/COLOR]: Europe','f',240,art+'/QAqdSDc.png',fanart)
        addLink('[COLOR red][I]EliteMember[/I][/COLOR]','','')*10
	#addLink('','','')<font color=".+?"><b>([^<]+)</b></b></font>CH 6 - Sky Sports 1 [HD] 24/7 </a></td></tr>
	match=re.compile('<font color=".+?"><b>([^<]+)</b.+?/font>.+?(\d+) - (.+?) </a></td></tr></b>').findall(link)                 
        for status,ch,name in match:
            if 'OFFLINE' in status:
                status='[COLOR red]'+status+'[/COLOR]'
            else:
                status='[COLOR green]'+status+'[/COLOR]'
            if len(ch) == 1:
                ch2= '0'+ch
            else:
                ch2=ch
            addDir(status+' '+name+' [COLOR orange]Channel:'+ch+'[/COLOR]','http://sportsaccess.se/'+BASE_URL+'.php?ch='+ch2,411,'http://sportsaccess.se/images/'+ch+'.png')
	#addDir('[COLOR blue]Schedule[/COLOR]','http://www.sportsaccess.se/forum/calendar.php?action=weekview&calendar=1',476,art+'/skyaccess.png')
    else:
                addLink2('-[B][COLOR red]Clear Cookies[/B][/COLOR]','url',358,artpath+'empty.png',fanart)
		addLink('[COLOR red][I]Free Member[/I][/COLOR]','','')
		addLink(' ','','')
		addLink2('-[B][COLOR blue]Twitter[/B][/COLOR] [COLOR white]Feed[/COLOR]','url',356,artpath+'twit.jpg',fanart)
		addLink('[COLOR ]Follow @SportsAccessSE to keep updated.[/COLOR]','','')
		addLink(' ','','')
		addDir2('Help Videos [I](includes "FreeMemberFix")[/I]','http://gdata.youtube.com/feeds/api/users/LoucaPSD/uploads?start-index=1&alt=rss',455,artpath+'121.png',fanart)
		addLink2('[COLOR]Sports[COLOR blue]Access[/COLOR].se Review[/COLOR]','7UKulB8CGFs',456,'https://i.ytimg.com/vi/7UKulB8CGFs/mqdefault.jpg',fanart,'')
		addLink('','','')
		addLink2('[COLOR white]Showing [COLOR red][I]Free Member[/I][/COLOR] after purchase?[/COLOR]','url',259,artpath+'empty.png',fanart)
		addLink2('	[I]	-Addon Settings (set to default, then press ok.)[/I]','url',239,artpath+'empty.png',fanart)
		addLink2('	[I]	-Login. (first clear settings to default)[/I]','url',555,artpath+'empty.png',fanart)	
		addLink2('[COLOR grey][I]	-Check Version[/I][/COLOR]','url',357,artpath+'empty.png',fanart)
		addLink2('[COLOR grey][I] To Purchase and upgrade to an [B][COLOR maroon]Elite Membership[/COLOR][/B] vist sportsaccess.net[COLOR white]  | [/COLOR][/I][/COLOR]'*10,'url','',artpath+'empty.png',fanart)
    if '<li><a title="Log Out"' in link2:
        i=0
        match=re.compile('<li><a href="([^"]+)"><center>(.+?)</a>').findall(link)                 
        for url,name in match:
                thumb=['http://i.imgur.com/nwW007z.png','http://i.imgur.com/PrsljU9.png','http://i.imgur.com/PehTqgO.png','http://i.imgur.com/uWOObK9.png','http://i.imgur.com/OOaeIzT.png']
                name = re.sub('(?sim)<[^>]*?>','',name)
                if 'http' not in url: url = 'http://nodetower.com'+url
                addDir(name,url,411,thumb[i])
                i=i+1
	addLink(' ','','')
	addLink2('-[B][COLOR red]Clear Cookies[/B][/COLOR]','url',358,artpath+'empty.png',fanart)
	addLink2('-[B][COLOR red]Expiry[/B][/COLOR] [COLOR white]Date[/COLOR]','url',256,artpath+'empty.png',fanart)	
	addDir2('-[B][COLOR red]Help[/B][/COLOR] [COLOR white]Videos[/COLOR]','http://gdata.youtube.com/feeds/api/users/LoucaPSD/uploads?start-index=1&alt=rss',455,artpath+'h.png',fanart)
	addLink2('-[B][COLOR blue]Twitter[/B][/COLOR] [COLOR white]Feed[/COLOR]','url',356,artpath+'twit.jpg',fanart)
	addLink('','','')
	addLink2('[COLOR grey][I]For support vist sportsaccess.net and submit a ticket [/I][/COLOR]','url','',artpath+'empty.png',fanart)
	addLink2('[COLOR grey][I]Check Addon Version[/I][/COLOR]','url',357,artpath+'empty.png',fanart)



def ytube():
	addLink2('[COLOR red][I]Free Member[/COLOR]Fix[/I]','eqriE5Tb2kk',456,'https://i.ytimg.com/vi/eqriE5Tb2kk/mqdefault.jpg',fanart,'')
	addLink2('Log in after purchase','roYXR5AZStY',456,'https://i.ytimg.com/vi/roYXR5AZStY/mqdefault.jpg',fanart,'')
	addLink2('Log in for Prometheus users','2VA9NQWerFM',456,'https://i.ytimg.com/vi/2VA9NQWerFM/mqdefault.jpg',fanart,'')
	addLink2('Fix 4:3 Video output (zoom video to remove black sides)','gArgxGwJopE',456,'https://i.ytimg.com/vi/gArgxGwJopE/mqdefault.jpg',fanart,'')
	
def Twitter():
        text = ''
        twit = 'https://script.google.com/macros/s/AKfycbyBcUa5TlEQudk6Y_0o0ZubnmhGL_-b7Up8kQt11xgVwz3ErTo/exec?569507192983023616'
        response = net().http_GET(twit)
        link = response.content
        link = link.replace('/n','')
        link = link.encode('ascii', 'ignore').decode('ascii').decode('ascii').replace('&#39;','\'').replace('&#xA0;','').replace('&#x2026;','')
        match=re.compile("<title>(.+?)</title>.+?<pubDate>(.+?)</pubDate>",re.DOTALL).findall(link)[1:]
        for status, dte in match:
            dte = dte[:-15]
            dte = '[COLOR blue][B]'+dte+'[/B][/COLOR]'
            text = text+dte+'\n'+status+'\n'+'\n'
        showText('[COLOR blue][B]@SportsAccessSE[/B][/COLOR]', text)
        quit()
	
def Set(id=AddonID):
    xbmc.executebuiltin('Addon.OpenSettings(%s)' % id)

def Fresh():
	xbmc.executebuiltin("XBMC.Container.Refresh")
	
def showText(heading, text):
    id = 10147
    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(500)
    win = xbmcgui.Window(id)
    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(500)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass

def clearCookies():
    dialog = xbmcgui.Dialog()
    if dialog.yesno('Mash Up', 'Are you sure you want to clear Cookies?','','','No', 'Yes'):
        import os
        cookie_file = os.path.join(datapath,'Cookies')
        ClearDir(xbmc.translatePath(cookie_file),True)
        xbmc.executebuiltin("XBMC.Notification(Clear Cookies,Successful,5000,"")")

def ClearDir(dir, clearNested = False):
    for the_file in os.listdir(dir):
        file_path = os.path.join(dir, the_file)
        if clearNested and os.path.isdir(file_path):
            ClearDir(file_path, clearNested)
            try: os.rmdir(file_path)
            except Exception, e: print str(e)
        else:
            try:os.unlink(file_path)
            except Exception, e: print str(e)
	
def PlayStream(url,iconimage):
    playback_url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % url
    ok=True
    xbmc.Player ().play(playback_url)

def account():
    user = selfAddon.getSetting('skyusername')
    passw = selfAddon.getSetting('skypassword')
    html = net().http_GET('http://bobbyrockshow.com/amember/member').content
    r = re.findall(r'<input type="hidden" name="(.+?)" value="(.+?)" />', html, re.I)
    post_data = {}
    post_data['amember_login'] = user
    post_data['amember_pass'] = passw
    for name, value in r:
        post_data[name] = value
    net().http_GET('http://bobbyrockshow.com/amember/login')
    net().http_POST('http://bobbyrockshow.com/amember/login',post_data)
    response = net().http_GET('http://bobbyrockshow.com/amember/member')
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    print link
    stat = ''
    user=re.compile('<div class="am-coll-content">(.+?)<').findall(link)[1]
    user = user+'\n'+' '
	
    accnt=re.compile('<li><strong>(.+?)</strong>(.+?)</li>').findall(link)
    for one,two in accnt:
        one = '[I][B]'+one+'[/I][/B]'
        stat = stat+' '+one+' '+two+'\n'
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR red]SportsAccess Membership[/COLOR]', '',stat,'')
	
def Login():
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR red]Free Member Fix[/COLOR]','- Open Addon Settings, set to Defauls, Then press OK','- Click Login, Re-Enter credentials and Log In',"- If you're still shown as a free member, open a support ticket on sportsaccess.net")
	
def Calendar(murl):
    setCookie()
    link  = OPENURL(murl,cookie='sportsaccess')
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    month=re.findall('(?sim)<td class="tcat smalltext" colspan="2">([^<]+?)</td>',link)
    match=re.findall('(?sim)<td class="trow_sep.+?>([^<]+?)</td></tr><tr><td class=".+?<span class="largetext">(\d+)</span></td><td class="trow1.+?>(.+?)</td>',link)
    for day,num,data in match:
       addLink('[COLOR blue]'+day+' '+num+' '+month[0]+'[/COLOR]','','')
       match2=re.findall('(?sim)<a href=".+?" class=" public_event" title="(.+?)">.+?</a>',data)
       for title in match2:
           addLink(title,'','')


def LISTCONTENT(murl,thumb):
    setCookie()
    link  = OPENURL(murl,cookie='sportsaccess')
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','').replace('%20','')
    if 'http://nodetower.com/7-SFE-SZE-HOSTACCESS/media/vod.php' == murl:
        response = net().http_GET('http://sportsaccess.se/forum/misc.php?page=Replays')
        link = response.content
        link = cleanHex(link)
        link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','').replace('%20','')
        
        match=re.compile('<a href="([^"]+)"><img src="([^"]+)" width=".+?alt="([^"]+)"></a>').findall(link)
        for url,thumb,name in match:
            if 'http' not in thumb:
                    thumb='http://sportsaccess.se/forum/'+thumb
            addDir(name,url,411,thumb)
    else:
	addLink2('[I][COLOR red]Refresh Links[/COLOR][/I]','url',555,artpath+'empty.png',fanart)	
        match=re.compile('<a href="(.+?)" class="btn btn-primary btn-sm" role="button">(.+?)</a>').findall(link)
        for url,name in match:
            if 'GO BACK' not in name and '1 Year Subscriptions' not in name and 'Live Broadcasts' not in name and '<--- Return To On Demand Guide' not in name and '**NEW**' not in name:
                name = re.sub('(?sim)<[^>]*?>','',name)
                if 'http' not in url:
                    url='http://sportsaccess.se/'+url
                addPlay(name,url,413,thumb)
	else:
		match=re.compile('<a href="(.+?)">(.+?)</a>').findall(link)
		for url,name in match:
			if '**NEW**' in name:
				name = re.sub('(?sim)<[^>]*?>','',name)
				if 'shoots' in url:
					addDir(name,url,411,thumb)
				if 'ecw' in url:
					addDir('**Under Construction** ECW Classic Hardcore PPV Section',url,411,thumb)
				

				


def get_link(murl):
    setCookie()
    link  = OPENURL(murl,cookie='sportsaccess')
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    m3u8=re.findall('<a href="([^"]+?.m3u8)">',link)
    m3u8B=re.findall("{file:'([^']+?.m3u8)'}",link)
    iframe=re.findall('<iframe src="(http://admin.livestreamingcdn.com[^"]+?)"',link)
    if m3u8:
        return m3u8[0]
    elif m3u8B:
        return m3u8B[0]
    elif 'euplayer' or 'usplayer' in murl:
        vlink=re.findall("""'file': "([^"]+)",""",link)
        return vlink[0]
    elif iframe:
        response = net().http_GET(iframe[0])
        link = response.content
        link = cleanHex(link)
        link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
        vlink=re.findall('file: "([^"]+?.m3u8)"',link)
        return vlink[0]
    else:
        swf=re.findall("src='([^<]+).swf'",link)[0]
        file=re.findall("file=(.+?)&",link)[0] 
        file=file.replace('.flv','')
        streamer=re.findall("streamer=(.+?)&",link)[0]
        if '.mp4' in file and 'vod' in streamer:
            file='mp4:'+file
            return streamer.replace('redirect','live')+' playpath='+file+' swfUrl='+swf+'.swf pageUrl='+murl
        else:
            return streamer.replace('redirect','live')+' playpath='+file+' swfUrl='+swf+'.swf pageUrl='+murl+' live=true timeout=20'
    
def PLAYLINK(mname,murl,thumb):
        ok=True
        stream_url = get_link(murl)     
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        listitem = xbmcgui.ListItem(mname, thumbnailImage=thumb)
        playlist.add(stream_url,listitem)
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playlist)
        return ok
		
      
                
				##################VERSION POPUP
def verPop():
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR red]Version[COLOR] [COLOR white]1.1.5[/COLOR]','-Moved from AutoUpdate to Repo','','')
       				

def addPlay(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage=" + urllib.quote_plus(iconimage)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage='', thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image',art+"fanart.jpg")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder = False)
        return ok

def addLink2(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok	
		
def addLink(name,url,iconimage):
    liz=xbmcgui.ListItem(name, iconImage=art+'/empty.png', thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('fanart_image',art+"fanart.jpg")
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)

def addDir2(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
	
def addDir(name, url, mode, iconimage):

        u  = sys.argv[0]

        u += "?url="  + urllib.quote_plus(url)
        u += "&mode=" + str(mode)
        u += "&name=" + urllib.quote_plus(name)
        u += "&iconimage=" + urllib.quote_plus(iconimage)

        liz = xbmcgui.ListItem(name, iconImage='', thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image',art+"fanart.jpg")

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,isFolder=True)
	

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param
              
params=get_params()
url=None
name=None
mode=None
iconimage=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
    iconimage = iconimage.replace(' ','%20')
except:
        pass

print "Mode: "+str(mode)
print "Name: "+str(name)
print "Thumb: "+str(iconimage)


if mode==None or url==None or len(url)<1:
        import threading
        MAINSA()
    
        
elif mode==411:LISTCONTENT(url,iconimage)
elif mode==413:PLAYLINK(name,url,iconimage)
elif mode==476:Calendar(url)
elif mode==455:ytube()
elif mode==456:PlayStream(url,iconimage)
elif mode==356:Twitter()
elif mode==357:verPop()
elif mode==358:clearCookies()
elif mode==256:account()
elif mode==259:Login()
elif mode==239:Set()
elif mode==555:Fresh()
elif mode==240:
    if selfAddon.getSetting("server-location") == "true":
        selfAddon.setSetting('server-location', 'false')
        print 'false'
    else:
        selfAddon.setSetting('server-location', 'true')
        print 'true'
    xbmc.executebuiltin("XBMC.Container.Refresh")

xbmcplugin.endOfDirectory(int(sys.argv[1]))
