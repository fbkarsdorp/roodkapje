all:
	@if [ -a db_repository ]; then rm -r db_repository; fi;
	@if [ -a annotations.db ]; then rm -r annotations.db; fi;

	@python db_create.py;
	@python db_migrate.py;
	@python fill_database.py;
	@python question_tree.py;