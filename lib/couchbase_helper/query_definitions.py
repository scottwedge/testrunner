import uuid
import random

FULL_SCAN_TEMPLATE = "SELECT {0} FROM %s"
RANGE_SCAN_TEMPLATE = "SELECT {0} FROM %s WHERE {1}"
FULL_SCAN_GROUP_BY_TEMPLATE = "SELECT {0} FROM %s GROUP by {2}"
RANGE_SCAN_GROUP_BY_TEMPLATE = "SELECT {0} FROM %s WHERE {1} GROUP BY {2}"
FULL_SCAN_ORDER_BY_TEMPLATE = "SELECT {0} FROM %s ORDER by {2}"
RANGE_SCAN_ORDER_BY_TEMPLATE = "SELECT {0} FROM %s where {1} ORDER BY {2}"
FULL_SCAN_COUNT_TEMPLATE = "SELECT count(*) FROM %s"
RANGE_SCAN_COUNT_TEMPLATE = "SELECT count(*) FROM %s WHERE {1}"
RANGE_SCAN_JOIN_TEMPLATE = "SELECT s1.{0},s2.{1} FROM %s as s1 JOIN %s as s2"
INDEX_CREATION_TEMPLATE =  "CREATE INDEX %s ON %s(%s)"
INDEX_DROP_TEMPLATE = "DROP INDEX %s.%s"
SIMPLE_INDEX="simple"
SIMPLE_ARRAY="simple_array"
ARRAY="array"
DUPLICATE_ARRAY="duplicate_array"
DISTINCT_ARRAY="distinct_array"
COMPOSITE_INDEX="composite"
GROUP_BY="groupby"
ORDER_BY="orderby"
RANGE_SCAN="range"
FULL_SCAN="full"
JOIN = "join"
EQUALS = "equals"
NOTEQUALS ="notequals"
NO_ORDERBY_GROUPBY="no_orderby_groupby"
GREATER_THAN="greater_than"
LESS_THAN="less_than"
AND = "and"
OR = "or"

class QueryDefinition(object):
	def __init__(self, name = "default", index_name = "Random", index_fields = [], index_creation_template = INDEX_CREATION_TEMPLATE,
		index_drop_template = INDEX_DROP_TEMPLATE, query_template = "", groups = [], index_where_clause = None, gsi_type = None):
		self.name = str(uuid.uuid4()).replace("-","")
		self.index_name = index_name
		self.index_fields = index_fields
		self.index_where_clause = index_where_clause
		self.index_creation_template = index_creation_template
		self.index_drop_template = index_drop_template
		self.query_template = query_template
		self.groups = groups

	def generate_index_create_query(self, bucket = "default", use_gsi_for_secondary = True,
	        deploy_node_info = None, defer_build = None, index_where_clause = None, gsi_type=None):
		deployment_plan = {}
		query = "CREATE INDEX {0} ON {1}({2})".format(self.index_name,bucket, ",".join(self.index_fields))
		if index_where_clause:
			query += " WHERE "+index_where_clause
		if use_gsi_for_secondary:
			query += " USING GSI "
			if gsi_type == "memdb":
				deployment_plan["index_type"] = "memdb"
		if not use_gsi_for_secondary:
			query += " USING VIEW "
		if deploy_node_info  != None:
			deployment_plan["nodes"] = deploy_node_info
		if defer_build != None:
			deployment_plan["defer_build"] = defer_build
		if len(deployment_plan) != 0 and use_gsi_for_secondary:
			query += " WITH " + str(deployment_plan)
		return query

	def generate_gsi_index_create_query_using_rest(self, bucket="default", deploy_node_info=None, defer_build=None,
												   index_where_clause=None, gsi_type="forestdb", expr_type="N1QL"):
		deployment_plan = {}
		ind_content = {}
		ind_content["name"] = self.index_name
		ind_content["bucket"] = "{0}".format(bucket)
		ind_content["secExprs"] = self.index_fields
		ind_content["using"] = gsi_type
		ind_content["exprType"] = "{0}".format(expr_type)
		if index_where_clause:
			ind_content["whereExpr"] = index_where_clause
		if deploy_node_info  != None:
			deployment_plan["nodes"] = deploy_node_info
		if defer_build != None:
			deployment_plan["defer_build"] = defer_build
		ind_content["with"] = str(deployment_plan)
		return ind_content

	def generate_index_drop_query(self, bucket = "default", use_gsi_for_secondary = True, use_gsi_for_primary = True):
		if "primary" in self.index_name:
			query =  "DROP PRIMARY INDEX ON {0}".format(bucket)
		else:
			query =  "DROP INDEX %s.%s" % (bucket, self.index_name)
		if use_gsi_for_secondary and "primary" not in self.index_name:
			query += " USING GSI"
		elif use_gsi_for_primary and "primary" in self.index_name:
			query += " USING GSI"
		if not use_gsi_for_secondary:
			query += " USING VIEW "
		return query

	def generate_query(self, bucket):
		if "join" in self.groups:
			return self.query_template % (bucket,bucket)
		return self.query_template % bucket

	def generate_query_with_explain(self, bucket):
		return ("EXPLAIN "+self.query_template) % bucket

	def add_group(self, group):
		self.groups.append(group)

class SQLDefinitionGenerator:
	def generate_simple_data_query_definitions(self):
		definitions_list = []
		index_name_prefix = "simple"+str(uuid.uuid4()).replace("-","")
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title",
				index_fields = ["job_title"],
				query_template = FULL_SCAN_TEMPLATE.format("*","name IS NOT NULL"),
				groups = [SIMPLE_INDEX, FULL_SCAN, "simple","isnotnull",NO_ORDERBY_GROUPBY]))
		return definitions_list

	def generate_employee_data_query_definitions(self):
		definitions_list = []
		index_name_prefix = "employee"+str(uuid.uuid4()).replace("-","")
		#emit_fields = "name, job_title, join_yr, join_mo, join_day"
		emit_fields = "*"
		and_conditions = ["job_title = \"Sales\"","job_title != \"Sales\""]
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"primary_index",
							 index_fields = [],
							 query_template = "SELECT * FROM %s",
							 groups = ["full_data_set","primary"], index_where_clause = ""))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title",
							 index_fields = ["job_title"],
							 query_template = RANGE_SCAN_ORDER_BY_TEMPLATE.format(emit_fields,"job_title IS NOT NULL","job_title,_id"),
							 groups = [SIMPLE_INDEX, FULL_SCAN, ORDER_BY, "employee","isnotnull"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title",
							 index_fields = ["job_title"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title = \"Sales\""),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,"employee"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title",
							 index_fields = ["job_title"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title = \"Sales\" ORDER BY job_title "),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, ORDER_BY, EQUALS,"employee"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title",
							 index_fields = ["job_title"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title != \"Sales\" ORDER BY _id"),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, NOTEQUALS,"employee"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title",
							 index_fields = ["job_title"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title = \"Sales\" or job_title = \"Engineer\" ORDER BY _id"),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, OR,"employee"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"join_yr",
							 index_fields = ["join_yr"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "join_yr > 2010 and join_yr < 2014 ORDER BY _id"),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, AND,"employee"], index_where_clause = " join_yr > 2010 and join_yr < 2014 "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"join_yr",
							 index_fields = ["join_yr"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "join_yr > 1999 ORDER BY _id"),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, GREATER_THAN,"employee"], index_where_clause = " join_yr > 2010 and join_yr < 2014 "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title_join_yr",
							 index_fields = ["join_yr","job_title"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title = \"Sales\" and join_yr > 2010 and join_yr < 2014"),
							 groups = [COMPOSITE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,AND,"employee"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title_join_yr",
							 index_fields = ["join_yr","job_title"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title = \"Sales\" and join_yr > 2010 and join_yr < 2014 ORDER BY job_title, _id"),
							 groups = [COMPOSITE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,OR,"employee"], index_where_clause = " job_title IS NOT NULL "))
		return definitions_list

	def generate_sabre_data_query_definitions(self):
		definitions_list = []
		index_name_prefix = "sabre_"+str(uuid.uuid4()).replace("-","")
		#emit_fields = "name, job_title, join_yr, join_mo, join_day"
		emit_fields = "*"
		and_conditions = ["job_title = \"Sales\"","job_title != \"Sales\""]
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"CurrencyCode",
							 index_fields = ["CurrencyCode"],
							 query_template = RANGE_SCAN_ORDER_BY_TEMPLATE.format(emit_fields,"CurrencyCode IS NOT NULL","CurrencyCode"),
							 groups = [SIMPLE_INDEX, FULL_SCAN, ORDER_BY, "sabre","isnotnull"], index_where_clause = " CurrencyCode IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"CurrencyCode",
							 index_fields = ["CurrencyCode"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "CurrencyCode = \"USD\""),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,"sabre"], index_where_clause = " CurrencyCode IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"CurrencyCode",
							 index_fields = ["CurrencyCode"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "CurrencyCode = \"USD\" ORDER BY CurrencyCode "),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, ORDER_BY, EQUALS,"sabre"], index_where_clause = " CurrencyCode IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"CurrencyCode",
							 index_fields = ["CurrencyCode"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "CurrencyCode != \"USD\""),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, NOTEQUALS,"sabre"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"CurrencyCode",
							 index_fields = ["CurrencyCode"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "CurrencyCode = \"USD\" or job_title = \"INR\""),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, OR,"sabre"], index_where_clause = " job_title IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"join_yr",
							 index_fields = ["join_yr"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "join_yr > 2010 and join_yr < 2014"),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, AND,"sabre"], index_where_clause = " join_yr > 2010 and join_yr < 2014 "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"join_yr",
							 index_fields = ["join_yr"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "join_yr > 1999"),
							 groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, GREATER_THAN,"sabre"], index_where_clause = " join_yr > 2010 and join_yr < 2014 "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"job_title_join_yr",
							 index_fields = ["join_yr","CurrencyCode"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "CurrencyCode = \"USD\" and join_yr > 2010 and join_yr < 2014"),
							 groups = [COMPOSITE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,AND,"sabre"], index_where_clause = " CurrencyCode IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"CurrencyCode_join_yr",
							 index_fields = ["join_yr","CurrencyCode"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title = \"USD\" and join_yr > 2010 and join_yr < 2014 ORDER BY job_title"),
							 groups = [COMPOSITE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,OR,"sabre"], index_where_clause = " CurrencyCode IS NOT NULL "))

		return definitions_list

	def generate_big_data_query_definitions(self):
		definitions_list = []
		index_name_prefix = "big_data_"+str(uuid.uuid4()).replace("-","")
		#emit_fields = "name, job_title, join_yr, join_mo, join_day"
		emit_fields = "*"
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"age",
							 index_fields = ["age"],
							 query_template = RANGE_SCAN_ORDER_BY_TEMPLATE.format(emit_fields,"age IS NOT NULL","age"),
							 groups = [SIMPLE_INDEX, FULL_SCAN, "big_data" ], index_where_clause = " age IS NOT NULL "))
		definitions_list.append(
			QueryDefinition(
				index_name=index_name_prefix+"name",
							 index_fields = ["name"],
							 query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "name != \"CRAP\" "),
							 groups = [SIMPLE_INDEX,RANGE_SCAN,"big_data"], index_where_clause = " name != \"CRAP\" "))

		return definitions_list

	def generate_employee_data_query_definitions_for_index_where_clause(self):
		definitions_list = []
		emit_fields = "*"
		and_conditions = ["job_title = \"Sales\"","job_title != \"Sales\""]
		definitions_list.append(
			QueryDefinition(
				index_name="simple_index_1",
				index_fields = ["job_title"],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title != \"Sales\""),
				groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,"employee"], index_where_clause = " job_title != \"Sales\" "))
		definitions_list.append(
			QueryDefinition(
				index_name="simple_index_2",
				index_fields = ["job_title"],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % " job_title = \"Sales\" "),
				groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, NOTEQUALS,"employee"], index_where_clause = " job_title = \"Sales\" "))
		definitions_list.append(
			QueryDefinition(
				index_name="simple_index_3",
				index_fields = ["join_yr"],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "join_yr > 1999"),
				groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, GREATER_THAN,"employee"], index_where_clause = " join_yr > 1999 "))
		definitions_list.append(
			QueryDefinition(
				index_name="composite_index_1",
				index_fields = ["join_yr","job_title"],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title = \"Sales\" and join_yr > 2010 and join_yr > 2014"),
				groups = [COMPOSITE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,AND,"employee"], index_where_clause = " job_title = \"Sales\" and join_yr > 2010 and join_yr > 2014 "))
		definitions_list.append(
			QueryDefinition(
				index_name="composite_index_2",
				index_fields = ["join_mo","job_title"],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title != \"Sales\" and join_mo > 0"),
				groups = [COMPOSITE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,OR,LESS_THAN,"employee"], index_where_clause = "job_title != \"Sales\" and join_mo > 0"))
		return definitions_list

	def generate_employee_data_query_definitions_for_index_expressions(self):
		definitions_list = []
		emit_fields = "*"
		and_conditions = ["job_title = \"Sales\"","job_title != \"Sales\""]
		definitions_list.append(
			QueryDefinition(
				index_name="simple_not_equals_",
				index_fields = ["job_title != \"Sales\""],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "job_title != \"Sales\""),
				groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, NOTEQUALS,"employee"], index_where_clause = " job_title != \"Sales\" "))
		definitions_list.append(
			QueryDefinition(
				index_name="simple_equals",
				index_fields = ["job_title = \"Sales\""],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % " job_title = \"Sales\" "),
				groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, EQUALS,"employee"], index_where_clause = " job_title = \"Sales\" "))
		definitions_list.append(
			QueryDefinition(
				index_name="simple_greater_than",
				index_fields = ["join_yr > 1999"],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "join_yr > 1999"),
				groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, GREATER_THAN,"employee"], index_where_clause = " join_yr > 1999 "))
		definitions_list.append(
			QueryDefinition(
				index_name="simple_less_than",
				index_fields = ["join_yr < 2014"],
				query_template = RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "join_yr < 2014"),
				groups = [SIMPLE_INDEX,RANGE_SCAN, NO_ORDERBY_GROUPBY, LESS_THAN,"employee"], index_where_clause = " join_yr < 2014 "))
		return definitions_list

	def generate_airlines_data_query_definitions(self):
		definitions_list = []

		#emit_fields = "name, job_title, join_yr, join_mo, join_day"
		emit_fields = "*"
		and_conditions = ["job_title = \"Sales\"","job_title != \"Sales\""]
		#Primary Index
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_primary_index",
							index_fields=[], query_template="SELECT * FROM %s",
							groups=["full_data_set","primary"],
							index_where_clause=""))
		#simple index on string
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_name",
							index_fields=["name"],
							query_template=RANGE_SCAN_ORDER_BY_TEMPLATE.format(
								emit_fields, "name IS NOT NULL","name,_id"),
							groups=["all", SIMPLE_INDEX, FULL_SCAN, ORDER_BY, "airlines", "isnotnull"],
							index_where_clause=" name IS NOT NULL "))
		#simple index on int
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_age",
							 index_fields=["age"],
							 query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "age = 40"),
							 groups=["all", SIMPLE_INDEX, NO_ORDERBY_GROUPBY, EQUALS],
							index_where_clause=" age IS NOT NULL "))
		#simple index on boolean
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_premium_customer",
							 index_fields=["premium_customer"],
							 query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " % "premium_customer = True"),
							 groups=["all", SIMPLE_INDEX, NO_ORDERBY_GROUPBY, EQUALS],
							index_where_clause=" premium_customer IS NOT NULL "))
		#array duplicate index on strings
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_travel_history_duplicate",
							index_fields=["ALL ARRAY t FOR t in `travel_history` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN travel_history SATISFIES t = \"India\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DUPLICATE_ARRAY, ORDER_BY, EQUALS,"airlines"],
							index_where_clause=" travel_history IS NOT NULL "))
		#array distinct index on strings
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_travel_history_distinct",
							index_fields=["DISTINCT ARRAY t FOR t in `travel_history` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN travel_history SATISFIES t = \"India\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_INDEX, SIMPLE_ARRAY, DISTINCT_ARRAY,
									ORDER_BY, EQUALS, "airlines"],
							index_where_clause=" travel_history IS NOT NULL "))
		#array duplicate index on alphanumeric
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_travel_history_code_duplicate",
							index_fields=["ALL ARRAY t FOR t in `travel_history_code` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN travel_history_code SATISFIES t = \"Ind123\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DUPLICATE_ARRAY, ORDER_BY, EQUALS,"airlines"],
							index_where_clause=" travel_history_code IS NOT NULL "))
		#array distinct index on alphanumeric
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_travel_history_code_distinct",
							index_fields=["DISTINCT ARRAY t FOR t in `travel_history_code` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN travel_history_code SATISFIES t = \"Ind123\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_INDEX, SIMPLE_ARRAY, DISTINCT_ARRAY,
									ORDER_BY, EQUALS, "airlines"],
							index_where_clause=" travel_history_code IS NOT NULL "))
		#array duplicate index on numbers
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_credit_cards_duplicate",
							index_fields=["ALL ARRAY t FOR t in `credit_cards` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN credit_cards SATISFIES t > 5000000 END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DUPLICATE_ARRAY, RANGE_SCAN, ORDER_BY,"airlines"],
							index_where_clause=" credit_cards IS NOT NULL "))
		#array distinct index on numbers
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_credit_cards_distinct",
							index_fields=["DISTINCT ARRAY t FOR t in `credit_cards` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN credit_cards SATISFIES t > 5000000 END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_INDEX, SIMPLE_ARRAY, DISTINCT_ARRAY,
									RANGE_SCAN, ORDER_BY, "airlines"],
							index_where_clause=" credit_cards IS NOT NULL "))
		#Duplcate array on boolean array
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_question_values_duplicate",
							index_fields=["ALL ARRAY t FOR t in `question_values` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s "
										   % "ANY t IN question_values SATISFIES t = True END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DUPLICATE_ARRAY, RANGE_SCAN, ORDER_BY, "airlines"],
							index_where_clause=" question_values IS NOT NULL "))
		#Distinct array on boolean array
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_question_values_duplicate",
							index_fields=["DISTINCT ARRAY t FOR t in `question_values` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN question_values SATISFIES t = True END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_INDEX, SIMPLE_ARRAY, DISTINCT_ARRAY,
									RANGE_SCAN, ORDER_BY, "airlines"],
							index_where_clause=" question_values IS NOT NULL "))
		#array distinct index on mixed data type
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_secret_combination",
							index_fields=["DISTINCT ARRAY t FOR t in `secret_combination` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN secret_combination SATISFIES t > \"a\" OR t > 1 END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_INDEX, SIMPLE_ARRAY, DISTINCT_ARRAY,
									RANGE_SCAN, ORDER_BY, OR, "airlines"],
							index_where_clause=" secret_combination IS NOT NULL "))
		#array index on items if object
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_booking_duplicate",
							index_fields=["ALL ARRAY t FOR t in TO_ARRAY(`booking`) END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN booking SATISFIES t.source = \"India\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DUPLICATE_ARRAY, RANGE_SCAN,
									ORDER_BY, EQUALS, "airlines"],
							index_where_clause=" booking IS NOT NULL "))
		#array index on items if object
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_booking_distinct",
							index_fields=["DISTINCT ARRAY t FOR t in TO_ARRAY(`booking`) END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN booking SATISFIES t.source = \"India\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DISTINCT_ARRAY, RANGE_SCAN,
									ORDER_BY, EQUALS, "airlines"],
							index_where_clause=" booking IS NOT NULL "))
		#Composite array distinct index
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_travel_history_name_age",
							index_fields=["DISTINCT ARRAY t FOR t in `travel_history` END", "name", "age"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
							   "ANY t IN travel_history SATISFIES t = \"India\" END AND name IS NOT NULL ORDER BY _id"),
							groups=["all", ARRAY, COMPOSITE_INDEX, DISTINCT_ARRAY, RANGE_SCAN,
									ORDER_BY, AND, EQUALS, "airlines"],
							index_where_clause=" travel_history IS NOT NULL "))
		#Simple array on scalar
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_name_array",
							index_fields=["DISTINCT ARRAY t FOR t in TO_ARRAY(`name`) END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN name SATISFIES t = \"Ciara\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DISTINCT_ARRAY, RANGE_SCAN,
									ORDER_BY, EQUALS, "airlines"],
							index_where_clause=" name IS NOT NULL "))
		#Duplicate array Index on Array of objects
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_travel_details_duplicate",
							index_fields=["ALL ARRAY t FOR t in `travel_details` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN travel_details SATISFIES t.country = \"India\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, DUPLICATE_ARRAY, RANGE_SCAN,
									ORDER_BY, EQUALS, "airlines"],
							index_where_clause=" travel_details IS NOT NULL "))
		#Distinct array Index on Array of objects
		index_name_prefix = "airlines_" + str(random.randint(100000, 999999))
		definitions_list.append(
			QueryDefinition(index_name=index_name_prefix + "_travel_details_distinct",
							index_fields=["DISTINCT ARRAY t FOR t in `travel_details` END"],
							query_template=RANGE_SCAN_TEMPLATE.format(emit_fields," %s " %
										   "ANY t IN travel_details SATISFIES t.country = \"India\" END ORDER BY _id"),
							groups=["all", ARRAY, SIMPLE_ARRAY, SIMPLE_INDEX, DISTINCT_ARRAY,
									RANGE_SCAN, ORDER_BY, EQUALS, "airlines"],
							index_where_clause=" travel_details IS NOT NULL "))
		return definitions_list

	def filter_by_group(self, groups = None, query_definitions = None):
		if not groups:
			groups = []
		if not query_definitions:
			query_definitions = []
		new_query_definitions = {}
		for query_definition in query_definitions:
			count = 0
			for group in query_definition.groups:
				for group_name in groups:
					if group_name == group:
						count += 1
			if count == len(groups) and query_definition.index_name \
					not in new_query_definitions.keys():
				new_query_definitions[query_definition.index_name] = query_definition
		return new_query_definitions.values()

	def _create_condition(self, fields = [], begin_range = [],
		begin_condition = None, end_range= [], end_condition = None):
		index = 0
		list = []
		for field in fields:
			condition_list=[]
			if begin_condition != None:
				condition_list.append (" ({0} {1} {2})".format(field, begin_condition,
					begin_range[index]))
			if end_condition != None:
				condition_list.append (" ({0} {1} {2})".format(field, end_condition, end_range[index]))
			list.append(" and ".join(condition_list))
			index +=1
		return " and ".join(list)
