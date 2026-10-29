# Import dependencies
import streamlit as st
import streamlit.components.v1 as components #to display the HTML code

import networkx as nx #Networkx for creating graph data
from pyvis.network import Network #to create the graph as an interactive html object

from src.CSPclass import CSPBasic
from src.algorithms import AC3

nodeColors={
    "empty":"white",
    "filled": "yellow"
}





def main():
    if "clicked" not in st.session_state:
        st.session_state["clicked"] = False
        
    if not st.session_state["clicked"]:
        # Set header title
        st.header("CSP: Simple Sudoku Example")
        st.header("_Initial Sudoku._", divider=True)
        
        sudokuNeighbors,sudokuDomains,sudokuConstraints1=getSudokuData()        
        basicSudokuCSP=CSPBasic(variables=sudokuNeighbors.keys(),neighbors=sudokuNeighbors, domains=sudokuDomains, constraints=sudokuConstraints1)

        buildGraph(basicSudokuCSP, nodeColors)
        
        if st.button("Run AC-3"):
            AC3(basicSudokuCSP)
            buildGraph(basicSudokuCSP, nodeColors, True)
            
        
        #st.button("Run AC-3", on_click= , args= [option])
        
         

        
def getSudokuData():
    var1=list("ABC")
    var2=range(1,4)
    filled={'A3':3, 'B1':9,'C3':1}

    vars=set()

    for letter in var1:
        for number in var2:
            vars.add(letter+str(number))
            sudokuNeighbors={}

    for letter in var1:
        for number in var2:
            sudokuNeighbors[letter+str(number)]=[]
            
    for key1 in sudokuNeighbors.keys():
        for key2 in sudokuNeighbors.keys():
            if key1!=key2:
                sudokuNeighbors[key1].append(key2)
            
    sudokuDomains={var:[filled[var]] if var in filled else [ch for ch in range(1,10)] for var in sudokuNeighbors.keys()}
    sudokuConstraints1 = lambda X, x, Y, y: x!=y
    
    return sudokuNeighbors,sudokuDomains,sudokuConstraints1

        
        
        
def buildGraph(SudokuCSP, nodeColors, ac3=False):
    netSudoku= Network(
                bgcolor ="#242020",
                font_color = "white",
                height = "750px",
                width = "100%"
                ) 
    
    nodeColorsDict={}
    nodeTitlesDict={}
    nodeLabelsDict={}
    nodes=list(SudokuCSP.variables)

    for node in nodes:
        if len(SudokuCSP.domains[node])==1:
            nodeColorsDict.setdefault(node,nodeColors["filled"])
            if ac3:
                nodeTitlesDict.setdefault(node,str(SudokuCSP.curr_domains[node][0]))
            else:
                nodeTitlesDict.setdefault(node,str(SudokuCSP.domains[node][0]))
            nodeLabelsDict.setdefault(node,str(SudokuCSP.domains[node][0]))           
        else:
            nodeColorsDict.setdefault(node,nodeColors["empty"])
            if ac3:
                string_list = [str(i) for i in SudokuCSP.curr_domains[node]]
               
            else:
                string_list = [str(i) for i in SudokuCSP.domains[node]]
            nodeTitlesDict.setdefault(node, ",".join(string_list) )
                
            nodeLabelsDict.setdefault(node,"")      
           
            
    x_coords = {}
    y_coords = {}

    for node in nodes:
        if node[0].lower()=="a":
            y_coords.setdefault(node,50)            
        elif node[0].lower()=="b":
            y_coords.setdefault(node,100)
        elif node[0].lower()=="c":
            y_coords.setdefault(node,150)
        x_coords.setdefault(node,int(node[1])*50)
           
            
    
    # initialize graph
    g = nx.Graph()
    
    # add the nodes
    for node in nodes:
        g.add_node(node, color=nodeColorsDict[node], size=10, title=nodeTitlesDict[node], label=nodeLabelsDict[node],  x_coord=x_coords[node],y_coord=y_coords[node])

    # add the edges
    print(SudokuCSP.neighbors)
    
    
    for nodeFrom in SudokuCSP.neighbors.keys():
        for nodeTo in SudokuCSP.neighbors[nodeFrom]:        
            if nodeFrom[0]==nodeTo[0]: # row const-s
                g.add_edge(nodeFrom,nodeTo, color="red")
            elif nodeFrom[1]==nodeTo[1]: # col const-s
                g.add_edge(nodeFrom,nodeTo, color="blue")
            else:
                g.add_edge(nodeFrom,nodeTo, color="green") # diag con-s
            
    print(g.edges)
    # generate the graph
    netSudoku.from_nx(g)
    #netSudoku.toggle_physics(False)
    
    netSudoku.save_graph('L6_SimpleSudoku.html')
    HtmlFile = open(f'L6_SimpleSudoku.html', 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height = 1200,width=1000)
    
    
    
    
if __name__ == '__main__':
    main()
        