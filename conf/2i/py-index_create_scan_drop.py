2i.indexscans_2i.SecondaryIndexingScanTests:
# INDEX Without WHERE And Expressions
    test_multi_create_query_explain_drop_index,groups=simple,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
    test_multi_create_query_explain_drop_index,groups=composite,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
# INDEX With Only Where
    test_multi_create_query_explain_drop_index_with_index_where_clause,groups=simple,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
    test_multi_create_query_explain_drop_index_with_index_where_clause,groups=composite:and:orderby:range,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
# INDEX with Only Expressions
    test_multi_create_query_explain_drop_index_with_index_expressions,groups=simple,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
    test_multi_create_query_explain_drop_index_with_index_expressions,groups=composite,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
# With INDEX with WHERE Clause and Expressions
    test_multi_create_query_explain_drop_index_with_index_expressions_and_where_clause,groups=simple,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
    test_multi_create_query_explain_drop_index_with_index_expressions_and_where_clause,groups=composite,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=20
# With MUTATIONS - INDEX without WHERE CLAUSE And EXPRESSIONS
    test_multi_create_query_explain_drop_index_with_mutations,groups=simple,dataset=default,doc-per-day=20,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc_ops=True,delete_ops_per=.5,run_async=True,scan_consistency=request_plus
    test_multi_create_query_explain_drop_index_with_mutations,groups=simple,dataset=default,doc-per-day=20,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc_ops=True,update_ops_per=.5,run_async=True,scan_consistency=request_plus
    test_multi_create_query_explain_drop_index_with_mutations,groups=simple,dataset=default,doc-per-day=20,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc_ops=True,expiry_ops_per=.5,run_async=True,scan_consistency=request_plus
    test_multi_create_query_explain_drop_index_with_mutations,groups=simple,dataset=default,doc-per-day=20,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc_ops=True,create_ops_per=.5,run_async=True,scan_consistency=request_plus
    test_multi_create_query_explain_drop_index_with_mutations,groups=simple,dataset=default,doc-per-day=20,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc_ops=True,create_ops_per=.3,delete_ops_per=.2,update_ops_per=.2,expire_ops_per=.1,run_async=True,scan_consistency=request_plus
    test_multi_create_query_explain_drop_index_with_mutations,groups=composite,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc_ops=True,create_ops_per=.5,delete_ops_per=.2,update_ops_per=.2,run_async=True,scan_consistency=request_plus
# PRIMARY INDEX
    test_multi_create_query_explain_drop_index_primary,groups=simple,dataset=default,use_gsi_for_primary=False,doc-per-day=20,run_async=True
    test_multi_create_query_explain_drop_index_primary,groups=primary,dataset=default,use_gsi_for_primary=True,doc-per-day=10,doc_ops=True,create_ops_per=.5,delete_ops_per=.2,update_ops_per=.2,run_async=True,scan_consistency=request_plus
# BUILD INDEX WITH CONCURRENT MUTATIONS
    test_multi_create_query_explain_drop_index_with_concurrent_mutations,groups=simple,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=50,doc_ops=True,create_ops_per=.5,delete_ops_per=.2,update_ops_per=.2,run_async=True,scan_consistency=request_plus
    test_multi_create_query_explain_drop_index_with_concurrent_mutations,groups=simple,dataset=default,use_gsi_for_primary=True,use_gsi_for_secondary=True,doc-per-day=100,doc_ops=True,create_ops_per=.5,delete_ops_per=.2,update_ops_per=.2,run_async=True,scan_consistency=request_plus