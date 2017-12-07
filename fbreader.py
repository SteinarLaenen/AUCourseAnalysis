# Loads data saved to feed.txt in json format
import json

def split_gen(st):
    """Takes file contents, splits based on elements in the list (i.e. json
    formatted posts (dic with message, id, and other relevant post details)"""
    st = st[1:] # Skip opening of list to prevent error
    while True:
        try:
            cur_ind = st.index(u'},') # Corresponds to end of a post in the list
            yield json.loads(st[:cur_ind + 1]) # Yield part corresponding to this index
            st = st[cur_ind+2:]
        except ValueError:
            cur_ind = st.index(u'}]')
            yield json.loads(st[:cur_ind+1])
            break # reached end of list
    
            
