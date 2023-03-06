# Name : arash ahmadi
# Id: 9717023103

from copy import deepcopy
import copy
import math
import xlsxwriter
import random as rnd
num_tasks = 5
num_machines = 3
maximum_check = 2000
nodes = []
tasks = []
count = 0
current_heuristic = 0
t = 0
time = 0
iter = 0
tasks_popu = []
nodes_popu = []
temp_nodes = []
rr1 = 0
rr2 = 0

class bcolors:
    HEADER = '\033[95m'
    # HEADER = ''
    OKBLUE = '\033[94m'
    # OKBLUE = ''
    OKCYAN = '\033[96m'
    # OKCYAN = ''
    OKGREEN = '\033[92m'
    # OKGREEN = ''
    WARNING = '\033[93m'
    # WARNING = ''
    FAIL = '\033[91m'
    # FAIL = ''
    ENDC = '\033[0m'
    # ENDC = ''

############################################# Task class

class Task:
 
    def __init__(self,amount,deadline,id):
        self.amount = amount
        self.deadline = deadline
        self.id = id

        self.run_time = 0
        self.assigned_machine = None
        self.finish_time = 0
        self.final_cost = 0
        self.crossed = 0

############################################# Node class

class Node:
    def __init__(self,speed,cost,id):
        self.speed = speed
        self.cost = cost
        self.id = id
        self.history = []
    
    def assignTask(self, task):

        global tasks, nodes
        
        task.assigned_machine = self.id
        task.run_time = (task.amount / self.speed) * 1000
        if len(self.history) != 0:
            task.finish_time = tasks[self.history[-1]].finish_time + task.run_time
        else:
            task.finish_time = task.run_time

        self.history.append(task.id)
        # print(f'In assign: Task {task.id} -> Node {self.id} new history: {self.history}')
        task.crossed =   task.finish_time - task.deadline
        task.final_cost = self.cost * (task.run_time/1000)
        
        return [task.finish_time, task.crossed, task.final_cost]

    def reassignTask(self,task):
        global tasks, nodes
        hist = nodes[task.assigned_machine].history
        # print(f'In reassign: Task {task.id} -> Node {self.id} history: {self.history}')
        ind = hist.index(task.id)
        hist.remove(task.id)
        task.run_time = (task.amount / self.speed) * 1000
        for i in range(ind, len(hist)):
            if i==0:
                tasks[hist[i]].finish_time = tasks[hist[i]].run_time
            else:
                tasks[hist[i]].finish_time = tasks[hist[i-1]].finish_time + tasks[hist[i]].run_time
            tasks[hist[i]].crossed =   tasks[hist[i]].finish_time - tasks[hist[i]].deadline
        
        self.assignTask(task)
        return ind

    def undoTheChange(self,task,ind):
        old_hist = nodes[task.assigned_machine].history
        old_hist.pop()
        task.assigned_machine = self.id
        task.run_time = (task.amount / self.speed) * 1000
        new_hist = self.history
        new_hist.insert(ind,task.id)

        if len(self.history) != 0:
            task.finish_time = tasks[self.history[-1]].finish_time + task.run_time
        else:
            task.finish_time = task.run_time
        
        for i in range(ind, len(new_hist)):
            if i==0:
                tasks[new_hist[i]].finish_time = tasks[new_hist[i]].run_time
            else:
                tasks[new_hist[i]].finish_time = tasks[new_hist[i-1]].finish_time + tasks[new_hist[i]].run_time
            tasks[new_hist[i]].crossed =   tasks[new_hist[i]].finish_time - tasks[new_hist[i]].deadline

        task.crossed =   task.finish_time - task.deadline
        task.final_cost = self.cost * (task.run_time/1000)
        return [task.finish_time, task.crossed, task.final_cost]

############################################# Getting input from user

def input_data():
    global tasks,nodes,num_tasks,num_machines,count
    tasks = []
    nodes = []
    num_tasks = 0
    num_machines = 0
    count = 0
    num_tasks = int(input(f'{bcolors.OKGREEN}Enter the number of tasks: {bcolors.ENDC}'))
    num_machines = int(input(f'{bcolors.OKGREEN}Enter the number of machines: {bcolors.ENDC}'))
    for i in range(0,num_tasks):
        tasks.append(Task(rnd.randint(1000,10000), rnd.randint(1000,10000),i))

    for i in range(0,num_machines):
        nodes.append(Node(rnd.randint(3000,10000), rnd.uniform(0.1,1),i))

############################################# Calculating heuristic

def heuristic(tasky):
    h1 = False
    flag = 0
    sum_of_costs = 0
    for task in tasky:
        sum_of_costs += task.final_cost
        if task.crossed > 0:
            flag += 1
    #if flag=0, it means all of the tasks have been done without reaching the deadline
    return [flag, sum_of_costs]


############################################# Hill climbing
def hill(isNormalHC):
    global tasks,nodes,current_heuristic,count,maximum_check
    change = 0
    count = 0
    if isNormalHC == 0:
        input_data()
    new_h = []
    for node in nodes:
        node.history = []
    
    for task in tasks:
        nodes[rnd.randint(0,num_machines-1)].assignTask(task)

    current_heuristic = heuristic(tasks)
    minimum_h = current_heuristic[0]
    minimum_c = current_heuristic[1]
    sideway_move = 0 
    while current_heuristic[0] != 0:
        
        count += 1
        if (count == maximum_check):
            break

        node = rnd.randint(0,num_machines-1)
        task = rnd.randint(0,num_tasks-1)
        node_backup = tasks[task].assigned_machine

        ind = nodes[node].reassignTask(tasks[task])
        current_heuristic = heuristic(tasks)
        change += 1
        if (current_heuristic[0] < minimum_h or (current_heuristic[0] == minimum_h and current_heuristic[1] < minimum_c)):
            minimum_h = current_heuristic[0]
            minimum_c = current_heuristic[1]
            count = 0
            
        else:
            if (current_heuristic[0] == minimum_h and current_heuristic[1] == minimum_c) :
                if sideway_move == 150:
                    change -=1
                    sideway_move = 0
                    nodes[node_backup].undoTheChange(tasks[task],ind)
                else:
                    sideway_move +=1
                
            else:
                change -=1
                sideway_move = 0
                nodes[node_backup].undoTheChange(tasks[task],ind)

    #if it doesn't have any tasks that reached deadline with a better cost, then print the solution

    if isNormalHC == 0:
        print_solution()
        
    else:
        return True

############################################# Random restart Hill climbing
def random_hill():
    global nodes,tasks,maximum_check,current_heuristic,count,temp_nodes
    temp_hu = []
    temp_tasks = []
    temp_nodes = []
    
    input_data()
    n = int(input(f'{bcolors.OKGREEN}Enter the number of restart points: {bcolors.ENDC}'))
    print()
    for i in range(0,n):
        allTasks = []
        allNodes = []
        count = 0
        print(f'{bcolors.OKGREEN}Pass {i} of doing hillclimbing{bcolors.ENDC}')
        hill(1)
        allTasks = copy.deepcopy(tasks)
        allNodes = copy.deepcopy(nodes)
        temp_tasks.append(allTasks)
        temp_nodes.append(allNodes)
        # del tt
        # del nn
        res = heuristic(tasks)
        temp_hu.append(res[0])
        print(f'{bcolors.OKCYAN}=========== DONE! , Deadlines reached : {res[0]} ==========={bcolors.ENDC}')

    
    max_task = min(temp_hu)
    ind = temp_hu.index(max_task)
    tasks = copy.deepcopy(temp_tasks[ind])
    nodes = copy.deepcopy(temp_nodes[ind])
    print(f'\nPass {ind} is the best solution. Printing the final solution:\n')
    print_solution()

############################################# Greedy
def greedy():
    global tasks,nodes,current_heuristic,count,maximum_check
    input_data()
    for node in nodes:
        node.history = []
    countt = 0
    nodes.sort(key=lambda x: x.cost, reverse=False)
    tasks.sort(key=lambda x: x.deadline, reverse=False)
    j = 0
    for node in nodes:
        node.id = j
        j+=1
    j = 0
    for task in tasks:
        task.id = j
        j+=1
    min_crossed=999
    countt_back = 0
    for task in tasks:
        # print(f'Iteration number {countt} for Task {task.id}')
        countt=0
        nodes[countt].assignTask(task)
        crossed = task.crossed
        while True:
            if countt == num_machines-1:
                nodes[countt_back].reassignTask(task)
                break
            else:   
                if crossed>0:
                    countt+=1
                    nodes[countt].reassignTask(task)
                    crossed = task.crossed
                else:
                    break
                if float(min_crossed) > crossed:
                    min_crossed = crossed
                    countt_back = countt

    print_solution()

############################################# Annealing

def annealing():
    
    global tasks,nodes,current_heuristic,count,maximum_check,t, time
    time = 0
    input_data()
    t = int(input(f'{bcolors.OKGREEN}Enter the primary temperature:{bcolors.ENDC} '))
    new_h = []
    for task in tasks:
        nodes[rnd.randint(0,num_machines-1)].assignTask(task)
    
    current_heuristic = heuristic(tasks)
    minimum_h = current_heuristic[0]
    minimum_c = current_heuristic[1]
    
    while True:
        time += 1

        node = rnd.randint(0,num_machines-1)
        task = rnd.randint(0,num_tasks-1)
        node_backup = tasks[task].assigned_machine

        ind = nodes[node].reassignTask(tasks[task])
        current_heuristic = heuristic(tasks)

        delta_E =  minimum_h - current_heuristic[0] + minimum_c - current_heuristic[1]
        t = t - 2 * time
        if (t <= 0):
            break

        print(f'Proccessing: {bcolors.FAIL}Temperatue: {t},{bcolors.ENDC}{bcolors.OKCYAN} Time: {time}{bcolors.ENDC}')
        if delta_E > 0:
            minimum_h = current_heuristic[0]
            minimum_c = current_heuristic[1]
            
        else:
            if(rnd.random() < math.exp(delta_E/t)):
                minimum_h = current_heuristic[0]
                minimum_c = current_heuristic[1]
            else:
                nodes[node_backup].undoTheChange(tasks[task],ind)
                
    #if the temperature became 0c, then stop the algorithm and print the solution
    print_solution()

############################################# Genetic

def genetic():
    init = 5
    global tasks,nodes,num_tasks,num_machines,count,tasks_popu,nodes_popu
    num_tasks = int(input(f'{bcolors.OKGREEN}Enter the number of tasks: {bcolors.ENDC}'))
    num_machines = int(input(f'{bcolors.OKGREEN}Enter the number of machines: {bcolors.ENDC}'))
    iter = int(input(f'{bcolors.OKGREEN}Enter the ammount of iterations: {bcolors.ENDC}'))
    n_popu = 300
    tasks = []
    nodes = []
    for i in range(0,num_tasks):
        tasks.append(Task(rnd.randint(1000,10000), rnd.randint(1000,10000),i))

    for i in range(0,num_machines):
        nodes.append(Node(rnd.randint(3000,10000), rnd.uniform(0.1,1),i))
    
    chromosome = []
    chromosome_ded = []

    for i in range(0,n_popu):
        chromosome.append([])
        for node in nodes:
            node.history = []
        for task in tasks:
            nodes[rnd.randint(0,num_machines-1)].assignTask(task)
            chromosome[i].append(task.assigned_machine)
        chromosome_ded.append(heuristic(tasks))

    chromosome_hu = []
    for item in chromosome_ded:
        chromosome_hu.append(round(((len(tasks)-item[0])/len(tasks))*100,0))
    # for item in chromosome_hu:
    #     print(item)

    for o in range(int(iter/2)):
        x = rnd.choices(chromosome, weights=tuple(chromosome_hu),k=1)
        y = rnd.choices(chromosome, weights=tuple(chromosome_hu),k=1)
        # print('Parents:')
        # print(x+'\n'+y)
        childs = reproduce(x[0],y[0])
        # print('Reproduced childs:')
        # print(childs[0]+'\n'+childs[1])
        if rnd.random() < 0.2:
            childs[0][rnd.randint(0,num_tasks-1)] = rnd.randint(0,num_machines-1)
        if rnd.random() < 0.2:
            childs[1][rnd.randint(0,num_tasks-1)] = rnd.randint(0,num_machines-1)

        for child in childs:
            for node in nodes:
                node.history = []
            for k in range(0,num_tasks):
                nodes[child[k]].assignTask(tasks[k])

            chromosome_ded.append(heuristic(tasks))
            chromosome_hu.append(round(((len(tasks)-chromosome_ded[-1][0])/len(tasks))*100,0))
            chromosome.append(child)
    
    find_max = max(chromosome_hu)
    indexx = chromosome_hu.index(find_max)
    # print('Final result:')
    # print(chromosome[indexx])
    for node in nodes:
        node.history = []
    for k in range(0,num_tasks):
        nodes[chromosome[indexx][k]].assignTask(tasks[k])
    print_solution()

############################################# Reproduce

def reproduce(x,y):
    line = rnd.randint(1,num_tasks-1)

    for i in range(0, line):
        temp = None

        temp = x[i]
        x[i] = y[i]
        y[i] = temp

    return [x,y]

def getHeuristic(tas):
    li = []
    for temp in tas:
        li.append(heuristic(tas)[0])
    return li

######################################Print the solution

def print_solution():
    global tasks
    for task in tasks:
        print(f'{bcolors.OKGREEN} Task {task.id} --> Machine {task.assigned_machine} {bcolors.ENDC}, {bcolors.OKCYAN} Runtime: {round(task.run_time,2)} {bcolors.ENDC}, {bcolors.OKBLUE} Finish time: {round(task.finish_time,2)} ms {bcolors.ENDC}, {bcolors.FAIL} Deadline: {round(task.deadline,2)} ms {bcolors.ENDC}, Final cost: {round(task.final_cost,2)}')

    res = heuristic(tasks)
    print(f'\n{num_tasks} Tasks and {num_machines} Nodes, {count} Neighbors checked', end='')
    if count == maximum_check:
        print(f' (Reached search limit)')
    else:
        print()
    print(f'Heuristic:  {res[0]} Tasks reached deadline, Performance:{bcolors.OKCYAN} {round((num_tasks-res[0])/num_tasks*100,2)}% {bcolors.ENDC}, total cost: {round(res[1],2)}')
    print()
    k=0
    cc = 0
    for node in nodes:
        sum = 0
        for item in node.history:
            new_run = (tasks[item].amount / node.speed) * 1000
            if new_run != tasks[item].run_time:
                print(f'Run time was miscalculated in Task {tasks[item].id}')
            sum += tasks[item].run_time
            if sum != tasks[item].finish_time:
                print(f'Response time was miscalculated in Task {item}')
                cc += 1
            
    # if cc==0 :
    #     print('Response times have been calculated correctly')
    
    first_time = True
    while True:
        if first_time:
            exportToXlsx()
            first_time = False
        print(f'\n{bcolors.OKGREEN}If you want to see more detail about the result, choose an option:{bcolors.ENDC}\n')
        print(f'{bcolors.WARNING}1. Save and view the bar chart in an excel file')
        print(f'2. Print the information of the created nodes and tasks')
        print(f"3. Print each node's queue list")
        print(f"4. Go back to menu {bcolors.ENDC}")
        choice = input()
        if choice == '1':
            exportToXlsx()
        
        elif choice == '2':
            for task in tasks:
                print(f'{bcolors.OKCYAN}Task {task.id} {bcolors.ENDC}: {bcolors.OKGREEN} {task.amount} MI, Deadline: {task.deadline}ms {bcolors.ENDC}')
            for node in nodes:
                print(f'{bcolors.HEADER}Node {node.id} {bcolors.ENDC}: {bcolors.OKBLUE} {node.speed} MIPS, Cost: {round(node.cost,2)} G$/S {bcolors.ENDC} ')
                
        elif choice == '3':
            print(f'\n{bcolors.OKBLUE}In each queue, you can see which task assigned to which node:{bcolors.ENDC}\n')
            for node in nodes:
                print(f'{bcolors.HEADER}Node {k}:{bcolors.ENDC} {bcolors.OKCYAN} {node.history} {bcolors.ENDC}')
                k += 1
            print(bcolors.ENDC)
        else:
            break
#############################################

def exportToXlsx():
    try:
        workbook = xlsxwriter.Workbook('Result.xlsx')   
        worksheet = workbook.add_worksheet()  

        bold = workbook.add_format({'bold': 1})  
        about = ['Arash ahmadi','9717023103']
        headings = ['Task', 'Node', 'Finishtime','Deadline']  
        
        li_tasks = []
        li_nodes = []
        li_finish = []
        li_deadlines = []
        for task in tasks:
            li_tasks.append(task.id)
            li_nodes.append(task.assigned_machine)
            li_finish.append(round(task.finish_time,2))
            li_deadlines.append(task.deadline)
        worksheet.set_column('A:D', 13)
        worksheet.write_row('A1', about, bold)  
        worksheet.write_row('A3', headings, bold)  
        worksheet.write_column('A4', li_tasks)  
        worksheet.write_column('B4', li_nodes)  
        worksheet.write_column('C4', li_finish)  
        worksheet.write_column('D4', li_deadlines)  
        chart1 = workbook.add_chart({'type': 'column'})  
        chart1.add_series({  
            'name':       "='Sheet1'!$C$3",  
            'categories': "='Sheet1'!$A$4:$A$"+str(num_tasks+3),  
            'values':     "='Sheet1'!$C$4:$C$"+str(num_tasks+3),
            'line':       {'color': 'green'},
        })  
        chart1.add_series({  
            'name':       "='Sheet1'!$D$3",  
            'categories': "='Sheet1'!$A$4:$A$"+str(num_tasks+3),  
            'values':     "='Sheet1'!$D$4:$D$"+str(num_tasks+3),
            'line':       {'color': 'red'},
        })  
        chart1.set_title ({'name': 'Results of analyzing finishtimes and deadlines'})  
        chart1.set_x_axis({'name': 'Tasks'})  
        chart1.set_y_axis({'name': 'Milliseconds'})  
        chart1.set_style(18)  
        worksheet.insert_chart('F2', chart1, {'x_scale': 2, 'y_scale': 2})  
        workbook.close()
        print(f'{bcolors.OKBLUE} Excel file (Result.xlsx) has been ctreated successfuly. it has been saved in the relative path')
    except:
        print(f"{bcolors.FAIL}Couldn't save the file because another program is using it or it's in read-only mode{bcolors.ENDC}")
############################################# Menu
def menu():

    print(f'\n{bcolors.OKCYAN}Task scheduling project')
    print('Name : Arash ahmadi \t Stud ID: 9717023103')
    print(f'----------------------------------------------\n {bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}Before assigning the tasks to machines, the algorithm must be chosen in order to machines start the procces\n')
    print(f'Which algorithm you want to use?\n{bcolors.ENDC}')
    print(f'1. Greedy')
    print('2. Hill-climbing')
    print('3. Random restart hill-climbing')
    print('4. Simulated annealing')
    print(f'5. Genetic algorithm\n')
    choice = input()
    if choice=="1":
        greedy()
    elif choice=="2":
        hill(0)
    elif choice=="3":
        random_hill()
    elif choice=="4":
        annealing()
    elif choice=="5":
        genetic()

    # input('\nPress any key to go back to menu')
    menu()

if __name__ == '__main__':
    menu()



    
        
    


        


