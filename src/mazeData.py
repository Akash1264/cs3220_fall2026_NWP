import numpy as np
import math
import random


import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from matplotlib.colors import ListedColormap

LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3

# Actions dictionary
actions_dict = {
    LEFT: 'left',
    UP: 'up',
    RIGHT: 'right',
    DOWN: 'down',
}

def makeMaze(n):
  size = (n,n)
  proba_0 =0.2 # resulting array will have 20% of zeros
  proba_food =0.1 # resulting array will have 10% of food pellets
  arrMaze=np.random.choice([0, 1,2], size=size, p=[proba_0, 1-proba_0-proba_food,proba_food])
  return arrMaze


def draw_maze(maze):
    fig, ax = plt.subplots()
    colors = sns.color_palette('coolwarm', len(np.unique(maze)))
    #print(colors)
    cmap = ListedColormap(colors)
    sns.heatmap(maze, cmap=cmap, annot=False, cbar=False)
    for i in range(maze.shape[0]):
      for j in range(maze.shape[1]):
        rect=patches.Rectangle((j, i), 1, 1, fill=False, edgecolor='yellow', lw=2)
        ax.add_patch(rect)
        #plt.gca().add_patch(patches.Rectangle((j, i), 1, 1, fill=False, edgecolor='yellow', lw=2))
        if i==0 and j==0:
            rect=patches.Rectangle((j, i), 1, 1, fill=True, color='pink')
            ax.add_patch(rect)
        if i==maze.shape[0]-1 and j==maze.shape[1]-1:
            rect=patches.Rectangle((j, i), 1, 1, fill=True, color='green')
            ax.add_patch(rect)

    plt.show()



def defineMazeActions(arr):
  n=arr.shape[0]
  mazeAvailableActions={}
  for i in range(n):
    for j in range(n):
      if i==0 and j==0:
        mazeAvailableActions.setdefault((i,j),[actions_dict[2],actions_dict[3]])
      elif i==0 and j==n-1:
        mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[3]])  
      elif i==n-1 and j==0:
        mazeAvailableActions.setdefault((i,j),[actions_dict[1],actions_dict[2]])
      elif i==n-1 and j==n-1:
        mazeAvailableActions.setdefault((i,j),[])
      elif i==0:
        mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[2],actions_dict[3]])
      elif i==n-1:
        mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[1],actions_dict[2]])
      elif j==0:
        mazeAvailableActions.setdefault((i,j),[actions_dict[1],actions_dict[2],actions_dict[3]])
      elif j==n-1:
        mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[1],actions_dict[3]])
      else:
        mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[1],actions_dict[2],actions_dict[3]])
  return mazeAvailableActions


def defineMazeAvailableActions(arr):
  n=arr.shape[0]
  mazeAvailableActions={}
  for i in range(n):
    for j in range(n):
      if i==0 and j==0:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[2],actions_dict[3]])
          if arr[i+1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[3])
          if arr[i,j+1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[2])
      elif i==0 and j==n-1:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[3]])
          if arr[i+1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[3])
          if arr[i,j-1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[0])
      elif i==n-1 and j==0:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[1],actions_dict[2]])
          if arr[i-1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[1])
          if arr[i,j+1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[2])
          
      elif i==n-1 and j==n-1:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[1]])
          if arr[i-1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[0])
          if arr[i,j-1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[1])
      elif i==0:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[2],actions_dict[3]])
          if arr[i,j-1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[0])
          if arr[i,j+1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[2])
          if arr[i+1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[3])
      elif i==n-1:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[1],actions_dict[2]])
          if arr[i,j-1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[0])
          if arr[i,j+1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[2])
          if arr[i-1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[1]) 
      elif j==0:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[1],actions_dict[2],actions_dict[3]])
          if arr[i-1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[1]) 
          if arr[i+1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[3])
          if arr[i,j+1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[2])
      elif j==n-1:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[1],actions_dict[3]])
          if arr[i,j-1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[0])
          if arr[i-1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[1]) 
          if arr[i+1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[3])
      else:
        if arr[i,j]==0:
          mazeAvailableActions.setdefault((i,j),[])
        else:
          mazeAvailableActions.setdefault((i,j),[actions_dict[0],actions_dict[1],actions_dict[2],actions_dict[3]])
          if arr[i-1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[1]) 
          if arr[i+1,j]==0:
            mazeAvailableActions[i,j].remove(actions_dict[3])
          if arr[i,j+1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[2])
          if arr[i,j-1]==0:
            mazeAvailableActions[i,j].remove(actions_dict[0])
        
  return mazeAvailableActions

def makeMazeTransformationModel(mazeActs):
    mazeStateSpace={}
    for key in mazeActs:
      for action in mazeActs[key]:
        if action=='left':
          x=key[0]
          y=key[1]-1
          mazeStateSpace.setdefault(key,{})[action]=(x,y)
        elif action=='up':
          x=key[0]-1
          y=key[1]
          mazeStateSpace.setdefault(key,{})[action]=(x,y)
        elif action=='right':
          x=key[0]
          y=key[1]+1
          mazeStateSpace.setdefault(key,{})[action]=(x,y)
        elif action=='down':
          x=key[0]+1
          y=key[1]
          mazeStateSpace.setdefault(key,{})[action]=(x,y)
      if len(mazeActs[key])==0:
        mazeStateSpace.setdefault(key,{})

    return mazeStateSpace

def mazeStatesRandomLocations(n):
  x = []
  y = []
  keyList=[]
  for i in range(n):
    for j in range(n):
      keyList.append((i,j))

  #print(keyList)
  for _ in range(len(keyList)):
    x.append(random.randint(0, n+1))
    y.append(random.randint(0, n+1))
  zipped = zip(x, y)
  return dict(zip(keyList, zipped))


def mazeStatesLocations(keyList): 
  x = []
  y = []
  
  for elem in keyList:
    x.append(elem[1]*100)
    y.append(elem[0]*100)
 
  zipped = zip(x, y)
  return dict(zip(keyList, zipped))



def intTupleTostr(t):
  return "-".join(str(item) for item in t)




