# Import dependencies
import streamlit as st
import streamlit.components.v1 as components #to display the HTML code
#from st_image_button import st_image_button
from st_clickable_images import clickable_images

import networkx as nx #Networkx for creating graph data
from pyvis.network import Network #to create the graph as an interactive html object
#from PIL import Image


from src.CSPclass import CSPBasic
from src.algorithms import AC3

nodeColors={
    "empty":"white",
    "filled": "yellow"
}

# List of image URLs or paths
image_urls = [
    "imgs/1.png",
    "imgs/3.png",
    "imgs/9.png",
    "imgs/empty.png"
    ]

imgCell={
    "1": 0,
    "3":1,
    "9":2,
    "empty":3
}

def runAC3(csp):
    st.session_state["clicked"]=True
    AC3(csp)
    return True





def main():
    if "clicked" not in st.session_state:
        st.session_state["clicked"] = False
        
    tab1, tab2 = st.tabs(["Initial Sudoku", "Graph of constraints"])
    
    
    sudokuNeighbors,sudokuDomains,sudokuConstraints1=getSudokuData()        
    basicSudokuCSP=CSPBasic(variables=sudokuNeighbors.keys(),neighbors=sudokuNeighbors, domains=sudokuDomains, constraints=sudokuConstraints1)
    ac3=False
    
    if st.session_state["clicked"]== False:        
        if st.button("Run AC-3"):
            st.session_state["clicked"]=True
            #st.text( st.session_state["clicked"])
            AC3(basicSudokuCSP)
            ac3=True
            
            
        
    
    with tab1:
        st.header("CSP: Simple Sudoku Example")
        
        # Define the number of rows you want
        num_rows = 3
        # Define the number of columns per row
        columns_per_row = 3
        vars=list(basicSudokuCSP.variables)
        print(vars)
        
        
        
        j=0
        
        for i in range(num_rows):
            # Create a set of columns for each row
            cols = st.columns(columns_per_row)
            
            # Place elements within each column of the current row
            for col_index, col in enumerate(cols):
                with col:
                    st.write(vars[j])
                    if ac3:
                        options=basicSudokuCSP.curr_domains[vars[j]]
                    else:
                        options=basicSudokuCSP.domains[vars[j]]
                    if len(options)==1:
                        st.text_input("filled",value=options[0], disabled =True, key=f"filled_cell_{vars[j]}", label_visibility="hidden")
                        #st.number_input("filled",value=options[0], disabled =True, key=f"filled_cell_{vars[j]}", label_visibility="hidden", step=None)
                    else:
                        st.selectbox("select",options,label_visibility="hidden", key=f"empty_cell_{vars[j]}")
                j+=1
        
            
        
    with tab2:
        
        buildGraph(basicSudokuCSP, nodeColors)
        
        if ac3:
            st.success("AC-3 applied. Check new domains")
            buildGraph(basicSudokuCSP, nodeColors, ac3)
        
 
            
        
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
        