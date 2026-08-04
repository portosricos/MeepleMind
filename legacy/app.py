import streamlit as st

# Normal display with simple text
st.write("Hello Streamlit")

st.header("This is the big header")
st.subheader("this is the smaller header")
st.caption("this is my caption")
st.text("Even smaller... What????!!")


st.markdown(
""" 
# this confuse me because its the same when I am doing a comment
## a bit smaller this is fun
### even smaller!!!

the music is fun. the *italic* and **bold** is easy to use

 """    
)

st.success("The futur is now")
st.warning("always be careful of your steps")
st.error("mistakes are in the past")


st.subheader("This is my image")
st.image('./media/Spiral_Galaxy-1.jpeg', caption='The galaxy is amazing', width=300)
# Spiral_Galaxy-1.jpeg

st.subheader("Display Video")
video_file=open('./media/file_example_MP4_480_1_5MG.mp4', 'rb').read()
st.video(video_file)
# file_example_MP4_480_1_5MG.mp4


st.sidebar.title("This is my sidebar")
with st.sidebar.form(key='my_form'):
    name = st.text_input('Username')
    password = st.text_input('Enter your password', type="password")
    submit_form = st.form_submit_button(label='Lets go!!!')
    if submit_form:
        st.success(f"Good job {name}. sshhhh i know your password that is {password}" )