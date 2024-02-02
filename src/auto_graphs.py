# Import Libraries
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import seaborn as sns
import numpy as np
import os

def define_text_color(patch):
    color_thr = 255*(patch.get_facecolor()[0]*0.299 + patch.get_facecolor()[1]*0.587 + patch.get_facecolor()[0]*0.114)
    if color_thr > 150:
        c = 'black'
    else:
        c = 'white'
    
    return c

def add_bar_labels(ax, labels):
    
    max = np.max([rect.get_height() for rect in ax.patches])
    
    for i, rect in enumerate(ax.patches):
        
        c = define_text_color(rect)
            
        bar_height = rect.get_height()
        if bar_height < (0.12*max):
            n_pad=0.035*max
            c='black'
        else:
            n_pad = -(0.08*max)
        
        ax.text(rect.get_x() + rect.get_width()/2, bar_height+n_pad, labels[i], ha='center', va='baseline', color = c, fontsize=12)

def generate_donut_graph(dados):
    
    sns.set_palette('Set2')
    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))
    percentagem = dados/dados.sum()*100

    wedges, text1 = plt.pie(dados, wedgeprops=dict(width=0.5), startangle=45)
    plt.legend(dados.index, loc='right', bbox_to_anchor=(0, 0., 1.6, 1))

    kw = dict(arrowprops=dict(arrowstyle="-", color='black'), zorder=0, va="center") # propriedades da

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        
        if percentagem[i] < 5:
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            if percentagem[i] <= 1:
                print(1-percentagem[i])
                ax.annotate('%.0f'%percentagem[i]+'%', xy=(x, y), xytext=(0.95*((i)*0.05+np.sign(x)), 0.95*(y+(i)*0.1)),
                    horizontalalignment=horizontalalignment, **kw)
            else:
                ax.annotate('%.0f'%percentagem[i]+'%', xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                        horizontalalignment=horizontalalignment, **kw)
        else:
            c = define_text_color(p)
            ax.annotate('%.0f'%percentagem[i]+'%', xy=(0.75*x, 0.75*y), horizontalalignment='center', verticalalignment='center', color=c)
            
    return fig, ax

def graph_risco_moradias(dados, fig_path = 'risco_moradias.png', regenerate=True):
    
    if not regenerate and os.path.exists(fig_path):
        return fig_path
    
    # Moradias x Risco
    fig = plt.Figure(figsize=(10,5))
    ax = sns.barplot(dados, x='Risco', y='Quantidade de Moradias', hue='colours', palette=list(dados['colours']), legend=False)
    ax.set_title('Classificação de risco das moradias')
    add_bar_labels(ax, dados['Quantidade de Moradias'])
    plt.tight_layout()
    ax.get_figure().savefig(fig_path)
    ax.get_figure().clf()
    
    return fig_path

def graph_setor_moradias(dados, fig_path = 'setor_moradias.png', regenerate=True):
    
    if not regenerate and os.path.exists(fig_path):
        return fig_path
    
    # Moradias x Setor
    fig = plt.Figure(figsize=(10,5))
    ax = sns.barplot(dados, x='Setor', y='Quantidade de Moradias')
    ax.get_figure()
    ax.set_title('Quantidade de moradias por setor de risco')
    plt.xticks(rotation = 45, horizontalalignment='right')
    add_bar_labels(ax, dados['Quantidade de Moradias'])
    plt.tight_layout()
    ax.get_figure().savefig(fig_path)
    ax.get_figure().clf()
    
    return fig_path

def graph_n_pavimentos(dados, fig_path = 'pav_imoveis.png', regenerate=True):
    
    if not regenerate and os.path.exists(fig_path):
        return fig_path
    
    # Moradias x Setor
    fig = plt.Figure(figsize=(10,5))
    ax = sns.barplot(dados, x='Número de pavimentos', y='Quantidade de Moradias')
    ax.set_title('Quantidade de pavimentos')
    # ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax.set_xticklabels([f'{num:.0f}' for num in dados['Número de pavimentos'][:-1]]+[dados['Número de pavimentos'].values[-1]])
    # plt.xticks(rotation = 45, horizontalalignment='right')
    add_bar_labels(ax, dados['Quantidade de Moradias'])
    plt.tight_layout()
    ax.get_figure().savefig(fig_path, bbox_inches='tight')
    ax.get_figure().clf()
    
    return fig_path

def graph_percentages(dados, graph_title, fig_path, regenerate=True):
    
    if not regenerate and os.path.exists(fig_path):
        return fig_path
    
    fig = plt.Figure(figsize=(10,5))
    fig, ax = generate_donut_graph(dados)
    ax.set_title(graph_title, position=(0.8, 1))
    plt.tight_layout()
    ax.get_figure().savefig(fig_path, bbox_inches='tight')
    ax.get_figure().clf()
    
    return fig_path

