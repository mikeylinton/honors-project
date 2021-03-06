import re as ree;
from graphviz import Digraph as Dot;
import argparse as ap
#authority={"name":[],"digit":[]}
G=Dot()

G.body.append('ranksep=".1"; nodesep=".1"; splines="line"; weight=1000; edge [dir=none fontsize=10 weight=1000]; node [shape=point fontsize=10 weight=1000]')

inputfile=open('sample.in', 'r')
count=0
#section=''
input_buildings=[]
while True:
	line=inputfile.readline().strip()
	if not line:	#EOF
		break
	count+=1
	if ree.search("^.*;$",line) and not ree.search("^#",line):
		items=ree.split(';+', line)
		items.remove('')
		for item in items:

			if section=="Environment":
				len_input_buildings=len(input_buildings)
				input_buildings.append([])
				building,rooms=item.split('[')
				building=building.replace(' ', '_')
				input_buildings[len_input_buildings].append(building)
				cluster_building='cluster_'+building
				rooms=rooms.strip(']')
				G.body.append('"'+building+'" [shape=none] [label="'+building.replace('_', ' ')+' lock"]')
				G.edge(building, '0('+building+')')
				G.body.append('[style=invis]')
				vars()[cluster_building]=Dot(cluster_building)
				vars()[cluster_building].body.append('label="'+building.replace('_', ' ')+'"')
				rooms=ree.split(',',rooms)
				for room in rooms:
					room=room.replace(' ', '_')
					vars()[cluster_building].body.append('"'+building+'_'+room+'" [shape=none] [label="'+room.replace('_', ' ')+' lock"]')
					vars()[cluster_building].edge(building+'_'+room, '0('+building+'_'+room+')')
					vars()[cluster_building].body.append('[style=invis]')
					input_buildings[len_input_buildings].append(room)
					cluster_building_room=cluster_building+'_'+room
					vars()[cluster_building_room] = Dot(cluster_building_room)
					vars()[cluster_building_room].body.append('label="'+room.replace('_', ' ')+'"')
#				if len_input_buildings > 0:
#					G.body.append('{ rank=same; edge[style=invis] "0('+input_buildings[len_input_buildings-1][0]+')" -> "0('+input_buildings[len_input_buildings][0]+')" }')

			if section=="Players":
				player,authority=item.split('(')
				authority=authority.strip(')')
				G.body.append('"'+player+'" [shape=none] [label="'+item+'"]')
				G.edge(player, '0('+player+')')
				G.body.append('{ rank=same; edge[style=invis] "'+building+'" -> "'+player+'" }')
				#G.body.append('{ rank=same; edge[style=invis] "0('+building+')" -> "0('+player+')" }')

			if section=="Main-flow":
				action,objects=item.split('(')
				objects=objects.strip(')')
				objects=ree.split(',',objects)
				
				if action=="unlock" or action=="lock" or action=="enter":
					
					is_building=False
					player=objects[0].replace(' ', '_')
					for items in input_buildings:
						if items[0]==objects[1].replace(' ', '_'):
							is_building=True;break
				
				if action=="enter":
					#objects[1] is a room/building i.e. enclave that can ocupy players
					if is_building:
						building=objects[1].replace(' ', '_')
						building_timeindex='timeindex_'+building
						cluster_building='cluster_'+building
						try:
							vars()[building_timeindex]+=1
							vars()[cluster_building].edge(str(vars()[building_timeindex]-1)+'('+building+')', str(vars()[building_timeindex])+'('+building+')')
							vars()[cluster_building].edge(str(vars()[building_timeindex]-1)+'('+player+')', str(vars()[building_timeindex])+'('+player+')')
						except:
							vars()[building_timeindex]=1
							#vars()[cluster_building].node('1('+building+')')
							G.edge('0('+building+')', '1('+building+')')
							vars()[cluster_building].node('1('+player+')')
						#G.body.append('"'+player+'" -> "'+str(vars()[building_timeindex])+'('+building+')" [style=dotted]')
						G.body.append('"0('+player+')" -> "'+str(vars()[building_timeindex])+'('+player+')" [style=dotted]')
					else: #enter room
						room=objects[1].replace(' ', '_')
						room_timeindex=('timeindex_'+building+'_'+room)
						cluster_building_room=cluster_building+'_'+room
						try:
							vars()[room_timeindex]+=1
							vars()[cluster_building_room].edge(str(vars()[room_timeindex]-1)+'('+building+'_'+room+')', str(vars()[room_timeindex])+'('+building+'_'+room+')')
						except:
							vars()[room_timeindex]=1
							vars()[cluster_building].edge('0('+building+'_'+room+')', '1('+building+'_'+room+')')
							vars()[cluster_building_room].node('1('+building+'_'+room+')')
						#vars()[cluster_building].body.append('"'+str(vars()[building_timeindex])+'('+building+')" -> "'+str(vars()[room_timeindex])+'('+room+')" [style=dotted]')

	elif ree.search("^\[.*\]$",line):
		item=line.strip('[').strip(']')
		sections=(
		"Environment",
		"Players",
		"Pre-conditions",
		"Main-flow",
		"Post-conditions")
		if item in sections:
			section=item	#;print(f"Line",count,":",line)
		else:
			print(f'\n',"Unknown section type",line,"on line",count,'\n',"Section types: [Environment] , [Players] , [Pre-conditions] , [Main-flow] , [Post-conditions]",'\n')
	else:
		if not ree.search("^#",line):
			print(f'\n',"BAD SYNTAX:",line,"on line",count,'\n')

for items in input_buildings:
	building='cluster_'+items.pop(0)
	for room in items:
		room=building+'_'+room
		vars()[building].subgraph(vars()[room])
	G.subgraph(vars()[building])
print(G)
outFile=open('out.dot', 'w')
outFile.write(str(G))
outFile.close()
#print(f"Total number of lines:",count)