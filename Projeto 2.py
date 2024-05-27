import numpy as np
import streamlit as st

def simplex_method(c, A_eq, b_eq, A_ineq, b_ineq):
    num_vars = len(c)
    num_eq_constraints = len(b_eq)
    num_ineq_constraints = len(b_ineq)
    
    # Adicionar variáveis de folga
    if num_eq_constraints > 0:
        A_eq = np.hstack([A_eq, np.eye(num_eq_constraints)])
    if num_ineq_constraints > 0:
        A_ineq = np.hstack([A_ineq, np.zeros((num_ineq_constraints, num_eq_constraints))])
    if num_eq_constraints > 0 and num_ineq_constraints > 0:
        A = np.vstack([A_eq, A_ineq])
    elif num_eq_constraints > 0:
        A = A_eq
    else:
        A = A_ineq

    c = np.concatenate([c, np.zeros(num_eq_constraints)])
    
    # Montar a tabela inicial do Simplex
    tableau = np.zeros((num_eq_constraints + num_ineq_constraints + 1, num_vars + num_eq_constraints + 1))
    tableau[:-1, :-1] = A
    tableau[:-1, -1] = np.concatenate([b_eq, b_ineq])
    tableau[-1, :-1] = -c
    
    while True:
        # Passo 1: Encontrar a coluna de entrada (variável entrando na base)
        pivot_col = np.argmin(tableau[-1, :-1])
        if tableau[-1, pivot_col] >= 0:
            break  # Solução ótima encontrada
        
        # Passo 2: Encontrar a linha de saída (variável saindo da base)
        ratios = np.divide(tableau[:-1, -1], tableau[:-1, pivot_col], 
                           out=np.full_like(tableau[:-1, -1], np.inf), where=tableau[:-1, pivot_col]>0)
        pivot_row = np.argmin(ratios)
        
        if np.isinf(ratios[pivot_row]):
            raise Exception("Problema não tem solução limitada.")
        
        # Passo 3: Pivotear
        pivot = tableau[pivot_row, pivot_col]
        tableau[pivot_row, :] /= pivot
        for r in range(len(tableau)):
            if r != pivot_row:
                tableau[r, :] -= tableau[r, pivot_col] * tableau[pivot_row, :]
    
    solution = np.zeros(num_vars)
    for i in range(num_vars):
        col = tableau[:, i]
        if sum(col == 1) == 1 and sum(col) == 1:
            row = np.where(col == 1)[0][0]
            solution[i] = tableau[row, -1]
    
    max_profit = -tableau[-1, -1]
    return solution, max_profit

st.title("Simplex Method Solver")

num_vars = st.number_input("Número de variáveis (n)", min_value=1, step=1)
num_eq_constraints = st.number_input("Número de restrições de igualdade (m1)", min_value=0, step=1)
num_ineq_constraints = st.number_input("Número de restrições de desigualdade (m2)", min_value=0, step=1)

c = []
A_eq = []
b_eq = []
A_ineq = []
b_ineq = []

if num_vars > 0:
    st.subheader("Coeficientes de lucro")
    for i in range(num_vars):
        c.append(st.number_input(f"Lucro unitário da variável {i+1}", key=f"c{i}"))

if num_eq_constraints > 0:
    st.subheader("Matriz de coeficientes das restrições de igualdade")
    for j in range(num_eq_constraints):
        row = []
        for i in range(num_vars):
            row.append(st.number_input(f"Coeficiente de x{i+1} na restrição de igualdade {j+1}", key=f"A_eq{j}{i}"))
        A_eq.append(row)
    st.subheader("Vetor de constantes das restrições de igualdade")
    for j in range(num_eq_constraints):
        b_eq.append(st.number_input(f"Constante da restrição de igualdade {j+1}", key=f"b_eq{j}"))

if num_ineq_constraints > 0:
    st.subheader("Matriz de coeficientes das restrições de desigualdade")
    for j in range(num_ineq_constraints):
        row = []
        for i in range(num_vars):
            row.append(st.number_input(f"Coeficiente de x{i+1} na restrição de desigualdade {j+1}", key=f"A_ineq{j}{i}"))
        A_ineq.append(row)
    st.subheader("Vetor de constantes das restrições de desigualdade")
    for j in range(num_ineq_constraints):
        b_ineq.append(st.number_input(f"Constante da restrição de desigualdade {j+1}", key=f"b_ineq{j}"))

if st.button("Resolver"):
    c = np.array(c)
    A_eq = np.array(A_eq) if num_eq_constraints > 0 else np.empty((0, num_vars))
    b_eq = np.array(b_eq) if num_eq_constraints > 0 else np.empty(0)
    A_ineq = np.array(A_ineq) if num_ineq_constraints > 0 else np.empty((0, num_vars))
    b_ineq = np.array(b_ineq) if num_ineq_constraints > 0 else np.empty(0)
    
    solution, max_profit = simplex_method(c, A_eq, b_eq, A_ineq, b_ineq)
    
    st.subheader("Solução ótima")
    for i in range(num_vars):
        st.write(f"x{i+1}: {solution[i]:.2f}")
    st.write(f"Lucro máximo: {max_profit}")
