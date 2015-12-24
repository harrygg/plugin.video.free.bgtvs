import sys, json, os

output = open("channels.txt", "w")

def GetProperty(i, prop):
	val = True if 'properties' in clist[i].keys() and prop in clist[i]['properties'] else False
	return val

def Enabled(i):
	return not GetProperty(i, "disabled")

def GetNumber():
	for i in range(1, len(clist) + 1):
		yield i
		
val = GetNumber()

filename = os.path.join('plugin.video.free.bgtvs\\resources\\lib\\channels.json')
with open(filename) as data_file: 
	clist = json.load(data_file)['channels']

for i in range(0, len(clist)):
	
		if "separator" not in clist[i]["id"]:
			if Enabled(i):
				line = "[b]%s.[/b] %s\n" % (val.next(), clist[i]["name"].encode('utf-8'))
			else:
				line = "[b]%s.[/b] %s - [b]%s[/b]\n" % (val.next(), clist[i]["name"].encode('utf-8'), "НЕРАБОТЕЩ")
		else:
			line = "\n[b]%s[/b]\n\n" % clist[i]["name"].encode('utf-8') 
		output.write( line )
		print line

output.close()
