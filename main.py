import pandas as pd
import numpy as np
import streamlit as st

import pendulum
import plotly.graph_objects as go

import time

from funcoes_horas import *


pendulum.set_locale('pt-br')


colunas = ['ID_Entrada', 'Mchn', 'ID_Funcionario', 'Nome', 'Modo', 'IOMd', 'Data', 'Hora']

meses = {1 : 'Janeiro',
2 : 'Fevereiro',
3 : 'Março',
4 : 'Abril',
5 : 'Maio',
6 : 'Junho',
7 : 'Julho',
8 : 'Agosto',
9 : 'Setembro',
10 : 'Outubro',
11 : 'Novembro',
12 : 'Dezembro'}

st.set_page_config(page_title = 'Horario dos Funcionários', layout = 'wide')

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)
st.title('Horário dos Funcionários')


col1, col2, col3, col4 = st.columns((1, 2, 1, 1))
col5, col6 = st.columns((1,1))

arquivo = col2.file_uploader('Insira o arquivo de horário dos funcionários', accept_multiple_files=False)

if arquivo:

    try:

        horarios = pd.read_table(arquivo, sep='\s+',
                                encoding='utf_16_le', header = 0, names = colunas,
                                parse_dates = [['Data', 'Hora']], keep_date_col = True)

        horarios['Ano'] = horarios['Data_Hora'].dt.year
        horarios['Mes'] = horarios['Data_Hora'].dt.month
        horarios['Dia'] = horarios['Data_Hora'].dt.day

        func = st.selectbox('Escolha o funcionário', options = sorted(horarios['Nome'].unique()))

        tabela = ultimo_mes(horarios, func)
        tabela_com_dia = coloca_nome_no_dia(tabela)
        agrupado = agrupa_dias_trabalhados(tabela_com_dia)
        horario_organizado = organizar_horario(agrupado)
        horas_calculadas = calcula_horas(horario_organizado)
        horas_trabalhadas = horas_trabalhadas_mes(horario_organizado)
        erros_funcionario = agrupa_erros(horario_organizado)

        mes_atual = tabela["Mes"].unique()[0]

        st.markdown(f'## O último mês completo que {func} trabalhou foi {meses[mes_atual]}')

        st.markdown(f'#### {func} trabalhou {horas_trabalhadas} neste mês')

        try:
                temp0 = horas_calculadas[['Nome', 'Data', 'Dia_Semana', 'Aviso', 'Hora_0', 'Hora_1', 'Hora_2', 'Hora_3']]
                
        except:
                temp0 = horas_calculadas[['Nome', 'Data', 'Dia_Semana', 'Aviso', 'Hora_0', 'Hora_1']]

        st.write(temp0)
        st.download_button(label='Download da Lista de Horas',
                           data=temp0.to_csv(index=False, na_rep='Sem data'),
                           file_name=f'Lista_Horas_{func}_{meses[mes_atual]}.csv')

        st.markdown(f'#### A quantidade de horas trabalhadas ao longo do mês')
        st.plotly_chart(figura_horas_trab(horas_calculadas), use_container_width=True)

        st.markdown(f'#### A quantidade de erros, ao usar o relógio de ponto, no mês')
        st.plotly_chart(figura_erros(erros_funcionario), use_container_width=True)

    except:
        st.subheader(f'Não há dados, nessa data, para {func}')


    st.markdown('---')
    st.subheader(f'Caso queira informações de outros anos/meses:')
    st.markdown('---')

    ano = int(st.selectbox('Escolha o Ano', options = sorted(horarios['Ano'].unique()), index = 1))

    mes = int(st.selectbox('Escolha o Mês', options = sorted(horarios['Mes'].unique())))

    if ano == 2000:
        st.subheader('Esse foi apenas um erro de leitura do relógio de ponto, escolha outro ano.')

    else:

        try:

            tabela = separa_funcionario(horarios, func, ano, mes)
            tabela_com_dia = coloca_nome_no_dia(tabela)
            agrupado = agrupa_dias_trabalhados(tabela_com_dia)
            horario_organizado = organizar_horario(agrupado)
            horas_calculadas = calcula_horas(horario_organizado)
            horas_trabalhadas = horas_trabalhadas_mes(horario_organizado)
            erros_funcionario = agrupa_erros(horario_organizado)

            mes_atual = tabela["Mes"].unique()[0]

            st.markdown(f'## O mês selecionado foi {meses[mes]} de {ano}')

            st.markdown(f'#### {func} trabalhou {horas_trabalhadas} neste mês')

            temp1 = horas_calculadas[['Nome', 'Data', 'Dia_Semana', 'Aviso', 'Hora_0', 'Hora_1', 'Hora_2', 'Hora_3']]

            st.write(temp1)
            st.download_button(label='Download da Lista de Horas',
                               data=temp1.to_csv(index=False, na_rep='Sem data'),
                               file_name=f'Lista_Horas_{func}_{meses[mes]}.csv')

            st.markdown(f'#### A quantidade de horas trabalhadas ao longo do mês')
            st.plotly_chart(figura_horas_trab(horas_calculadas), use_container_width=True)

            st.markdown(f'#### A quantidade de erros, ao usar o relógio de ponto, no mês')
            st.plotly_chart(figura_erros(erros_funcionario), use_container_width=True)

        except:
            st.markdown(f'## O mês selecionado foi {meses[mes]} de {ano}')
            st.subheader(f'Não há dados, nessa data, para {func}')



else:
    col1.write('Insira seu arquivo!')
