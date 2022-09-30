# Testing procedures

Careful: It is important that the tests be conducted in the order shown in the scripts below:

## Main testing

Test on docker.

```bash
docker-compose up -d --build # As when running
docker-compose exec app python -m pytest app/tests/test_health_check.py app/tests/test_users.py -k 'test_health_check or test_sign_up or test_login or test_login_with_invalid_password or test_user_detail or test_user_detail_forbidden_without_token or test_user_detail_forbidden_with_expired_token' # Test suite 1
pytest app/tests/test_posts.py -k 'test_create_post or test_create_post_forbidden_without_token or test_posts_list or test_post_detail or test_update_post or test_update_post_forbidden_without_token' # Test suite 2
docker-compose down # If it needs to be brought down
```

## Alternative: Testing on local environment

Test app on local environment, using docker for the rest (DB, etc.).

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres pgadmin # As when running
source activate_venv # If not already active
alembic upgrade head # If DB not already up to date
pytest app/tests/test_health_check.py app/tests/test_users.py -k 'test_health_check or test_sign_up or test_login or test_login_with_invalid_password or test_user_detail or test_user_detail_forbidden_without_token or test_user_detail_forbidden_with_expired_token' # Test suite 1
pytest app/tests/test_posts.py -k 'test_create_post or test_create_post_forbidden_without_token or test_posts_list or test_post_detail or test_update_post or test_update_post_forbidden_without_token' # Test suite 2
```
