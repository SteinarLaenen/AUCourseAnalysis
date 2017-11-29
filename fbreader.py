# Reader that, upon being called reads all data and writes it to a file in json
# format (Runs in python2)
import sys
import facebook


if __name__ == '__main__':
    token = sys.argv[1] # token provided in command line
    graph = facebook.GraphAPI(access_token=token)
    target_group = graph.search(type="group", q="The excellent and diverse people of AUC")
    group_id = target_group[u'data'][0][u'id']
    feed = graph.get_all_connections(id=group_id, connection_name='feed')
    
    
