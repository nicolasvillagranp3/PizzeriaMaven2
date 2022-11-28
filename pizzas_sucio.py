import pandas as pd
from dateutil.parser import parse
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import math
import random
import numpy as np


def extract():
    pizzas = pd.read_csv('pizzas.csv', encoding='latin1')
    pizza_types = pd.read_csv('pizza_types.csv', encoding='latin1')
    orders = pd.read_csv('orders_2016.csv', encoding='latin1', sep=';')
    order_details = pd.read_csv(
        'order_details_2016.csv', encoding='latin1', sep=';')
    return pizzas, pizza_types, orders, order_details


def transform(pizzas, pizza_types, orders, order_detail):
    random.seed(999)
    global fechas
    fechas = ['01/01/2016']

    def cambiar(a):
        if a[:-2].isdigit():
            return fechas[-1]

        else:
            fechas.append(a)
            return a

    def limpiar(a):
        if type(a) == float and math.isnan(a):  # Cuidado con los Nans
            return a
        else:
            return a.replace('@', 'a').replace('3', 'e').replace('0', 'o').replace(' ', '_').replace('-', '_')

    def quitar_caracteres(a):
        if type(a) == float and math.isnan(a):
            return a
        if a[-2] == '_':
            return a[:-2]
        else:
            return a

    def add_pizza(a):
        if type(a) == float:
            # Fijamos que sea una pizza random mediana
            return random.choice(mas_pedidos)+'_m'
        else:
            return a
    # Datos que no me interesan para los ingredientes semanales.
    orders.pop('time')
    orders = orders.sort_values('order_id')
    orders['date'] = orders['date'].fillna('1000').apply(cambiar).apply(parse)
    orders.index = pd.Series([i for i in range(len(orders))])
    # Supongo que cuando hay -1 y -2 es porque querian poner un 1 o un 2. No tendria sentido tener un pedido con cero pizzas.
    order_details['quantity'] = order_details['quantity'].str.lower().replace(
        {'one': 1, 'two': 2, '-1': 1, '-2': 2}).astype('float').interpolate()
    order_details.loc[0, 'quantity'] = 1
    # He aplicado una interpolacion (lineal por defecto) sobre los datos, teniendo antes que remplazar los strings y convertir todo a float (los nans son floats)
    # y no se pueden castear a enteros.
    order_details['pizza_id'] = order_details['pizza_id'].apply(limpiar)
    mas_pedidos = order_details['pizza_id'].apply(
        quitar_caracteres).value_counts()[:10].index  # Cojo las 10 pizzas mas vendidas
    order_details['pizza_id'] = order_details['pizza_id'].apply(add_pizza).apply(
        limpiar)  # Relleno los huecos con las pizzas más pedidas
    orders['date'] = orders['date'].apply(
        lambda x: x.week % 53)  # Solo me interesa la semana
    return orders, order_details, pizza_types, pizzas


def get_ingredients(pizza_types):
    ingredientes_por_pizza = {}
    # Va a contener el numero total de ingredientes por semana.
    ingredientes = {}
    for i in range(len(pizza_types)):
        aux = pizza_types.ingredients[i].split(',')
        ingredientes_por_pizza[pizza_types.pizza_type_id[i]] = [
            i.strip() for i in aux]
        for j in aux:
            if j not in ingredientes:
                ingredientes[j.strip()] = [0 for i in range(53)]
    return ingredientes, ingredientes_por_pizza


def sum_ingredients(pizza, ingredientes, ingredientes_por_pizza, semana, cantidad):
    tamaños = {'s': 1, 'm': 1.4, 'l': 1.8}
    if pizza not in ingredientes_por_pizza:
        suma = tamaños[pizza[-1]]
        if pizza[len(pizza)-2:] == 'xl':  # Este es el caso particular de The greek
            if pizza[-3] == 'x':
                pizza = pizza[:-4]
                suma = 2.2
            else:
                pizza = pizza[:-3]
                suma = 2.8
        else:
            pizza = pizza[:-2]
    else:
        suma = 1.4
    for h in ingredientes_por_pizza[pizza]:
        ingredientes[h][semana] += cantidad*suma
    return ingredientes


def get_ingredients_per_week(orders, order_details, pizza_types):
    ingredientes, ingredientes_por_pizza = get_ingredients(pizza_types)
    for i in range(len(order_details)):
        info = order_details.loc[i]
        semana = list(orders[orders.order_id == info['order_id']]['date'])[0]
        pizza = info['pizza_id']
        cantidad = info['quantity']
        ingredientes = sum_ingredients(
            pizza, ingredientes, ingredientes_por_pizza, semana, cantidad)
    return convert_int(ingredientes)


def convert_int(ingredientes):
    for i in ingredientes:
        for j in range(len(ingredientes[i])):
            ingredientes[i][j] = math.ceil(ingredientes[i][j])
    return ingredientes


def create_report(pizza_types, orders, order_details, pizzas):
    csvs = [pizza_types, orders, order_details, pizzas]
    raiz = Element('Tipologia_Datos_Pizzeria_Maven')
    pizzas1 = SubElement(raiz, 'pizzas.csv', {'rows': '96'})
    orders1 = SubElement(raiz, 'orders.csv', {'rows': '21350'})
    order_details1 = SubElement(raiz, 'order_details.csv', {'rows': '48620'})
    pizza_types1 = SubElement(raiz, 'pizza_types.csv', {'rows': '32'})
    jerar_xml = [pizza_types1, orders1, order_details1, pizzas1]
    for i in range(len(csvs)):
        columnas = csvs[i].columns.values
        for j in columnas:
            col1 = SubElement(jerar_xml[i], str(j))
            tipo = str(csvs[i][j].dtype)
            a = csvs[i][j].isnull().value_counts()
            # si no ha encontrado ningun null que el numero total sea cero.
            n_nulls = a[1] if len(a) > 1 else 0
            atribs1 = SubElement(col1, 'atribs', {
                                 'type': f'{tipo}', 'nulls': f'{n_nulls}'})
    return raiz


def load(ingredientes):
    # Lo pasamos a CSV
    pd.DataFrame(ingredientes).to_csv(
        'out/compra_semanal_2017.csv', header=True, index=None)


def load_report(raiz, antes=0):
    arbol = ET.ElementTree(raiz)
    if antes:
        arbol.write('out/reporte_tipologia_antes.xml')
    else:
        arbol.write('out/reporte_tipologia_despues.xml')


if __name__ == '__main__':
    # Me parecia buena idea hacer dos informes: Uno antes de transformar y otro despues, para que se pueda ver
    # el cambio bien reflejado.
    pizzas, pizza_types, orders, order_details = extract()
    raiz = create_report(pizzas, pizza_types, orders, order_details)
    load_report(raiz, 1)
    orders, order_details, pizza_types, pizzas = transform(
        pizzas, pizza_types, orders, order_details)
    ingredientes = get_ingredients_per_week(orders, order_details, pizza_types)
    raiz = create_report(pizzas, pizza_types, orders, order_details)
    load_report(raiz)
    load(ingredientes)
