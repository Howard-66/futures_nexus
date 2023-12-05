import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 创建一个简单的数据框
df = pd.DataFrame({
 'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 'Bananas'],
 'Amount': [4, 1, 2, 2, 4, 5],
 'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
})

# 使用st.sidebar添加一个选择框
chart_type = st.sidebar.selectbox('选择一个图表类型', ['柱状图', '线图'])
st.line_chart(df['Amount'])

# 根据用户的选择创建相应类型的图表
if chart_type == '柱状图':
 fig = go.Figure(data=[
 go.Bar(
     x=df['Fruit'],
     y=df['Amount'],
     name='SF',
     marker_color='rgb(58,200,225)'
 ),
 go.Bar(
     x=df['Fruit'],
     y=df['Amount'],
     name='Montreal',
     marker_color='rgb(8,81,156)'
 )
 ])
elif chart_type == '线图':
 fig = go.Figure(data=[
 go.Scatter(
     x=df['Fruit'],
     y=df['Amount'],
     mode='lines+markers',
     name='SF',
     marker_color='rgb(58,200,225)'
 ),
 go.Scatter(
     x=df['Fruit'],
     y=df['Amount'],
     mode='lines+markers',
     name='Montreal',
     marker_color='rgb(8,81,156)'
 )
 ])

# 创建一个空的容器
# chart_container = st.empty()

# 创建一个网格布局，并在每个列中添加不同的Streamlit元素
col1, col2 = st.columns((2, 1))

# 在第一列中显示图表
col1.plotly_chart(fig)

# 在第二列中显示DataFrame的原始数据
# col2.dataframe(df)

# 创建一个饼图
pie_fig = go.Figure(data=[go.Pie(labels=df['Fruit'], values=df['Amount'])])

# 在第一列中再次显示图表
col2.plotly_chart(pie_fig)