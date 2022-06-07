import pendulum
import pandas as pd
import plotly.graph_objects as go

def ultimo_mes(tabela, nome):

  df = tabela[(tabela['Nome'] == nome)].reset_index(drop = True)

  agrupamento = df.groupby(['Ano','Mes'])

  lista_meses = []

  for name, data in agrupamento:
    lista_meses.append(name)

  lista_meses.sort(reverse=True)

  try:
    funcionario = tabela[(tabela['Nome'] == nome) & (tabela['Ano'] == lista_meses[1][0]) & (tabela['Mes'] == lista_meses[1][1])].reset_index(drop = True)

  except IndexError:
    funcionario = tabela[(tabela['Nome'] == nome) & (tabela['Ano'] == lista_meses[0][0]) & (tabela['Mes'] == lista_meses[0][1])].reset_index(drop = True)

  except:
    return 'Deu algum erro, fala com o Thalliton'

  return funcionario


def separa_funcionario(df, nome, ano, mes):
    funcionario = df[(df['Nome'] == nome) & (df['Ano'] == ano) & (df['Mes'] == mes)].reset_index(drop=True)

    return funcionario


def coloca_nome_no_dia(tabela):
    tabela['Dia_Semana'] = tabela['Data'].apply(lambda x: pendulum.parse(x).format('dddd').capitalize())
    tabela = tabela.reindex(columns=['Nome', 'Data_Hora', 'Dia_Semana', 'Data', 'Hora', 'Ano', 'Mes', 'Dia'])
    return tabela


def agrupa_dias_trabalhados(df):
    dias_trab = df.groupby(by=['Data'])

    return dias_trab


def organizar_horario(tabela):
    tab = []

    for name, data in tabela:

        dtemp = pd.DataFrame(data)

        qtd_passada = 0

        for i in dtemp['Data_Hora'].iloc:
            dtemp[f'Hora_{qtd_passada}'] = str(i)

            qtd_passada += 1

        dtemp.drop_duplicates(subset=['Data'], inplace=True)

        if dtemp['Dia_Semana'].values[0] != 'Sábado' and qtd_passada < 4:

            dtemp['Obs'] = 'Não passou a quantidade de vezes certa'

        elif dtemp['Dia_Semana'].values[0] == 'Sábado' and qtd_passada > 2:

            dtemp['Obs'] = 'Não passou a quantidade de vezes certa'

        else:

            dtemp['Obs'] = 'Ok'

        dtemp['Vezes'] = qtd_passada

        horarios_arrumados = arrumar_horas(dtemp, qtd_passada)

        tab.append(horarios_arrumados)

        tabela = pd.concat(tab).reset_index(drop=True)

        tabela.fillna('Sem data', inplace=True)

    try:
        tabela = tabela[
            ['Nome', 'Data_Hora', 'Dia_Semana', 'Data', 'Hora', 'Ano', 'Mes', 'Dia', 'Hora_0', 'Hora_1', 'Hora_2',
             'Hora_3', 'Obs', 'Vezes']]

    except KeyError:
        tabela = tabela[
            ['Nome', 'Data_Hora', 'Dia_Semana', 'Data', 'Hora', 'Ano', 'Mes', 'Dia', 'Hora_0', 'Hora_1', 'Obs',
             'Vezes']]

    except:
        return 'Deu algum erro, fala com o Thalliton'

    return tabela


def arrumar_horas(dtemp, qtd_passada):
    for i in range(0, qtd_passada - 1):

        hora1 = pendulum.parse(dtemp[f'Hora_{i}'].values[0])
        hora2 = pendulum.parse(dtemp[f'Hora_{i + 1}'].values[0])

        if hora1.diff(hora2).in_minutes() < 30:

            if i == 0:
                try:
                    dtemp[f'Hora_{i + 1}'] = dtemp[f'Hora_{i + 2}']
                except:
                    pass

                try:
                    dtemp[f'Hora_{i + 2}'] = dtemp[f'Hora_{i + 3}']
                except:
                    pass

                try:
                    dtemp[f'Hora_{i + 3}'] = dtemp[f'Hora_{i + 4}']
                except:
                    pass

            else:
                dtemp[f'Hora_{i}'] = dtemp[f'Hora_{i + 1}']
                try:
                    dtemp[f'Hora_{i + 1}'] = dtemp[f'Hora_{i + 2}']
                except:
                    pass

                try:
                    dtemp[f'Hora_{i + 2}'] = dtemp[f'Hora_{i + 3}']
                except:
                    pass

                try:
                    dtemp[f'Hora_{i + 3}'] = dtemp[f'Hora_{i + 4}']
                except:
                    pass

    return dtemp


def calcula_horas(tabela):
    index = 0
    almoco = pendulum.duration(hours=1, minutes=30)
    passou_uma_vez = pendulum.duration(hours=8)

    for i in tabela.iloc:

        if i.Vezes == 1:
            tabela.loc[index, 'Horas'] = passou_uma_vez
            tabela.loc[index, 'Segundos_trab'] = passou_uma_vez.total_seconds() / 3600
            tabela.loc[index, 'Horas_Trabalhadas'] = str(passou_uma_vez)
            tabela.loc[index, 'Aviso'] = 'Passou somente 1 vez'

        if i.Vezes == 2:

            if i.Dia_Semana == 'Sábado':

                hora0 = pendulum.parse(f"{i['Hora_0']}/{i['Hora_1']}")
                tabela.loc[index, 'Horas'] = hora0.as_interval()
                tabela.loc[index, 'Segundos_trab'] = hora0.total_seconds() / 3600
                tabela.loc[index, 'Horas_Trabalhadas'] = str(hora0.as_interval())
                tabela.loc[index, 'Aviso'] = 'Ok'

            else:
              
              hora0 = pendulum.parse(f"{i['Hora_0']}/{i['Hora_1']}")
              
              if hora0.in_minutes() < 360:
                
                tabela.loc[index, 'Horas'] = hora0.as_interval()
                tabela.loc[index, 'Segundos_trab'] = (hora0.as_interval()).total_seconds() / 3600
                tabela.loc[index, 'Horas_Trabalhadas'] = str(hora0.as_interval())
                tabela.loc[index, 'Aviso'] = 'Trabalhou Meio Periodo / Passou somente 2 vezes'
                
              else:
                
                tabela.loc[index, 'Horas'] = hora0.as_interval() - almoco
                tabela.loc[index, 'Segundos_trab'] = (hora0.as_interval() - almoco).total_seconds() / 3600
                tabela.loc[index, 'Horas_Trabalhadas'] = str(hora0.as_interval() - almoco)
                tabela.loc[index, 'Aviso'] = 'Passou somente 2 vezes'

        if i.Vezes == 3:
            hora0 = pendulum.parse(f"{i['Hora_0']}/{i['Hora_2']}")

            tabela.loc[index, 'Horas'] = hora0.as_interval() - almoco
            tabela.loc[index, 'Segundos_trab'] = (hora0.as_interval() - almoco).total_seconds() / 3600
            tabela.loc[index, 'Horas_Trabalhadas'] = str(hora0.as_interval() - almoco)
            tabela.loc[index, 'Aviso'] = 'Passou somente 3 vezes'

        if i.Vezes >= 4:
            hora0 = pendulum.parse(f"{i['Hora_0']}/{i['Hora_1']}")
            hora1 = pendulum.parse(f"{i['Hora_2']}/{i['Hora_3']}")

            tabela.loc[index, 'Horas'] = hora0 + hora1
            tabela.loc[index, 'Segundos_trab'] = (hora0 + hora1).total_seconds() / 3600
            tabela.loc[index, 'Horas_Trabalhadas'] = str(hora0 + hora1)
            tabela.loc[index, 'Aviso'] = 'Ok'

        index += 1

    return tabela


def horas_trabalhadas_mes(tabela):
    return converte_horas(tabela['Horas'].sum().total_seconds())


def converte_horas(seg):
    horas = seg // 3600

    resto_horas = seg % 3600

    minutos = resto_horas // 60

    segundos = resto_horas % 60

    return (f'''{horas} hora(s), {minutos} minuto(s), {segundos} segundo(s)''')


def agrupa_erros(tabela):
    return tabela.groupby(by=["Aviso"]).size().reset_index(name="Counts")

def calcula_mes(df):
  inicio_mes = pendulum.parse(str(hras_trab['Data_Hora'][0])).start_of('month')
  fim_mes = pendulum.parse(str(hras_trab['Data_Hora'][0])).end_of('month')
  mes = pendulum.parse(f'{inicio_mes}/{fim_mes}')

  return mes 

def calcula_dias(mes):
  dias = {'Segunda-feira' : 0, 'Terça-feira': 0, 'Quarta-feira': 0, 'Quinta-feira': 0, 'Sexta-feira': 0, 'Sábado': 0, 'Domingo': 0}
  for dt in mes.range('days'):
    dias[dt.format('dddd').capitalize()] += 1

  return dias

def calcula_horas_por_mes(dias):
  total = 0
  horas_por_dia = {}

  for i, j in dias.items():

    if i == 'Sábado':
      horas = (pendulum.duration(hours=4, minutes = 30) * j).in_seconds()
      total += horas

    elif i == 'Domingo':
      horas = (pendulum.duration(hours=0) * j).in_seconds()

    else:
      horas = (pendulum.duration(hours=8) * j).in_seconds()
      total += horas

    horas_por_dia[i] = horas

  horas_por_dia['Total'] = total
  
  return horas_por_dia

def figura_horas_trab(tabela):
    fig = go.Figure()

    for i in tabela.iloc:

        if i['Dia_Semana'] == 'Sábado':

            fig.add_trace(go.Bar(x=[i['Dia']],
                                 y=[i['Segundos_trab']],
                                 name=str(i['Dia']),
                                 hovertemplate=f" Dia = {i['Dia']}<br> Dia_Semana = {i['Dia_Semana']} <br> Horas_Trabalhadas = {i['Horas_Trabalhadas']} <br>",
                                 marker_color='orange',
                                 ))


        elif i['Dia_Semana'] != 'Sábado' and i['Segundos_trab'] <= 6:
            fig.add_trace(go.Bar(x=[i['Dia']],
                                 y=[i['Segundos_trab']],
                                 name=str(i['Dia']),
                                 hovertemplate=f" Dia = {i['Dia']}<br> Dia_Semana = {i['Dia_Semana']} <br> Horas_Trabalhadas = {i['Horas_Trabalhadas']} <br>",
                                 marker_color='red'))

        else:

            fig.add_trace(go.Bar(x=[i['Dia']],
                                 y=[i['Segundos_trab']],
                                 name=str(i['Dia']),
                                 hovertemplate=f" Dia = {i['Dia']}<br> Dia_Semana = {i['Dia_Semana']} <br> Horas_Trabalhadas = {i['Horas_Trabalhadas']} <br>",
                                 marker_color='gray'))

    fig.update_layout(
        width=1000,
        height=500,
        margin=dict(l=15, r=15, b=15, t=15),
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=15))

    fig.update_xaxes(type='category', tickfont=dict(color='black', size=14))
    fig.update_yaxes(tickvals=[0, 2, 4, 6, 8, 10, 12], tickfont=dict(color='black', size=14))

    return fig


def figura_erros(tabela):
    fig = go.Figure()

    for i in tabela.iloc:
        fig.add_trace(go.Bar(x=[i['Aviso']],
                             y=[i['Counts']],
                             text=f"{i['Counts']} dias",
                             textposition='outside',
                             textfont_color = 'black'))

        #fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

    fig.update_layout(
        width=1000,
        height=500,
        margin=dict(l=15, r=15, b=15, t=15),
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=15))

    fig.update_xaxes(type='category', tickfont=dict(color='black', size=14))
    fig.update_yaxes(tickfont=dict(color='black', size=14))

    return fig
