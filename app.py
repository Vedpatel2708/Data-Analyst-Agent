import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from groq import Groq

# Initialize Groq client
client = Groq(api_key='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')

# Function to read CSV and Excel files
def read_tabular_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")

# Function to extract text from PDF
def read_pdf(file):
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

# Function to extract text from DOCX
def read_docx(file):
    doc = Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

# Function to extract text from images
def read_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

# Function to handle file processing
def handle_file(file):
    if file.name.endswith(('.csv', '.xlsx')):
        return read_tabular_file(file)
    elif file.name.endswith('.pdf'):
        return read_pdf(file)
    elif file.name.endswith('.docx'):
        return read_docx(file)
    elif file.name.endswith(('.png', '.jpg', '.jpeg')):
        return read_image(file)
    else:
        raise ValueError("Unsupported file format")

# Function to ask questions using Groq
def ask_question(prompt):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

# Function to create a visualization
def create_visualization(data, plot_type, x_col, y_col):
    if isinstance(data, pd.DataFrame):
        fig, ax = plt.subplots(figsize=(10, 6))
        if plot_type == 'Bar':
            sns.barplot(x=x_col, y=y_col, data=data, ax=ax)
        elif plot_type == 'Line':
            sns.lineplot(x=x_col, y=y_col, data=data, ax=ax)
        elif plot_type == 'Scatter':
            sns.scatterplot(x=x_col, y=y_col, data=data, ax=ax)
        ax.set_title(f"{plot_type} plot of {y_col} vs {x_col}")
        st.pyplot(fig)
    else:
        st.error("Invalid data for visualization")

# Streamlit UI
def main():
    st.title("Data Analyst Agent with Groq")
    st.write("Upload a file and ask questions or generate visualizations.")

    uploaded_file = st.file_uploader("Upload your file", type=['csv', 'xlsx', 'pdf', 'docx', 'png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        try:
            data = handle_file(uploaded_file)
            if isinstance(data, pd.DataFrame):
                st.write("### Preview of Data:")
                st.write(data.head())

                # Visualization section
                st.write("### Create a Visualization:")
                x_col = st.selectbox("Select X Column", data.columns)
                y_col = st.selectbox("Select Y Column", data.columns)
                plot_type = st.selectbox("Select Plot Type", ["Bar", "Line", "Scatter"])
                if st.button("Generate Plot"):
                    create_visualization(data, plot_type, x_col, y_col)

            else:
                st.write("### Extracted Text:")
                st.write(data[:500])  # Limit display to first 500 characters

                # Q&A section
                st.write("### Ask a Question:")
                question = st.text_input("Enter your question:")
                if st.button("Get Answer"):
                    if question.strip():
                        with st.spinner("Generating answer..."):
                            response = ask_question(f"Context: {data}\nQuestion: {question}")
                            st.write("**Answer:**", response)
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()