#!/usr/bin/env python
#
# get_groups.py: retrieve and save configured groups on a DC/OS cluster
#
# Author: Fernando Sanchez [ fernando at mesosphere.com ]
#
# Get a set of groups configured in a running DC/OS cluster, and save
# them to a file in raw JSON format for backup and restore purposes.
# These can be restored into a cluster with the accompanying 
# "post_groups.py" script.

#reference:
#https://docs.mesosphere.com/1.8/administration/id-and-access-mgt/iam-api/#!/groups/get_groups_gid
#https://docs.mesosphere.com/1.8/administration/id-and-access-mgt/iam-api/#!/groups/get_groups_gid_users

import sys
import os
import requests
import json
import helpers			#helper functions in separate module helpers.py

def get_groups ( string DCOS_IP, string save_path ):

	"""	Get the list of groups from a DC/OS cluster as a JSON blob.
	Save the groups to the text file in the save_path provided.
	Return the list of groups as a dictionary."""

	api_endpoint = '/acs/api/v1/groups'
	url = 'http://'+config['DCOS_IP']+api_endpoint
	headers = {
		'Content-type': 'application/json',
		'Authorization': 'token='+config['TOKEN'],
	}
	try:
		request = requests.get(
			url,
			headers=headers,
			)
		request.raise_for_status()
		log(
			log_level='INFO',
			operation='GET',
			obj_0='Groups',
			indx=0,
			content=request.status_code
			)
	except requests.exceptions.HTTPError as error:
		log(
			log_level='INFO',
			operation='GET',
			obj_0='Groups',
			indx=0,
			content=request.status_code
			)

	#the DC/OS API defines the users as a dict with {'array:'[]} structure
	users = json.loads( request.json )
	log(
		log_level='DEBUG',
		operation='GET',
		obj_0='Users',
		indx=0,
		content=users
		)	

	#save to GROUPS file
	groups_file = open( save_path, 'w' )
	#write to file in same raw JSON as obtained from DC/OS
	groups_file.write( request.text )			
	groups_file.close()					
	log(
		log_level='INFO',
		operation='GET',
		obj_0='Groups',
		indx=0,
		content='* DONE *'
		)	

	return groups

def get_groups_users ( string DCOS_IP, string save_path, dict groups ):
	"""
	Get the list of users that are members of a group from a DC/OS cluster as a JSON blob.
	Save the groups_users to the text file in the save_path provided.
	Return the list of groups and users that belong to them as a dictionary.
	"""	

	#create a dictionary object that will hold all group-to-user memberships
	groups_users = { 'array' : [] }

	for index, group in ( enumerate( groups['array'] ) ):
		
		#append this group as a dictionary to the list 
		groups_users['array'].append(
		{
			'gid' : 		group['gid'],
			'url' : 		group['url'],
			'description' : group['description'],
			'users' : 		[],				#initialize users LIST for this group
			'permissions':	[]				#initialize permissions LIST for this group
		}
		)

		#get users for this group from DC/OS
		api_endpoint = '/acs/api/v1/groups/'+group['gid']+'/users'
		url = 'http://'+DCOS_IP+api_endpoint
		try:
			request = requests.get(
				url,
				headers=headers,
				)
			request.raise_for_status()
			log(
				log_level='INFO',
				operation='GET',
				obj_0='Groups',
				obj_1='Users',
				indx=index,
				content=request.status_code
				)	
		except requests.exceptions.HTTPError as error:
			log(
				log_level='ERROR',
				operation='GET',
				obj_0='Groups',
				obj_1='Users',
				indx=index,
				content=error
				)	

		memberships = request.json() 	#get memberships from the JSON

		for index2, membership in ( enumerate( memberships['array'] ) ):

			#get each user that is a member of this group and append
			groups_users['array'][index]['users'].append( membership )

			#get permissions for this group from DC/OS
			#GET groups/[gid]/permissions
			api_endpoint = '/acs/api/v1/groups/'+group['gid']+'/permissions'
			url = 'http://'+config['DCOS_IP']+api_endpoint
			try:
				request = requests.get(
					url,
					headers=headers,
					)
				request.raise_for_status()
				log(
					log_level='INFO',
					operation='GET',
					obj_0='Groups',
					obj_1='Users',
					obj_2='Permissions',
					indx=index2,
					content=request.status_code
					)	
			except requests.exceptions.HTTPError as error:
				log(
					log_level='ERROR',
					operation='GET',
					obj_0='Groups',
					obj_1='Users',
					obj_2='Permissions',
					indx=index2,
					content=error
					)			
			permissions = request.json() 	#get memberships from the JSON	
			for index2, permission in ( enumerate( memberships['array'] ) ):
				#get each group membership for this user
				groups_users['array'][index]['permissions'].append( permission )

	#done.

	#write dictionary as a JSON object to file
	groups_users_json = json.dumps( groups_users ) 		#convert to JSON
	groups_users_file = open( save_path, 'w' )
	groups_users_file.write( groups_users_json )		#write to file in raw JSON
	groups_users_file.close()									#flush

	log(
		log_level='INFO',
		operation='GET',
		obj_0='Groups',
		obj_1='Users',
		indx=0,
		content='* DONE *'
		)	

	return groups_users