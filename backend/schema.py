import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import ToDoItem as ToDoItemModel
from graphql_relay import from_global_id
from database import db_session

class ToDoItem(SQLAlchemyObjectType):
    class Meta:
        model = ToDoItemModel
        interfaces = (graphene.relay.Node, )

class CreateToDoItem(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        time = graphene.DateTime()
        image_url = graphene.String()

    todo = graphene.Field(lambda: ToDoItem)

    def mutate(self, info, title, description=None, time=None, image_url=None):
        # Get user ID from context (passed from the Keycloak authentication)
        user_info = info.context.get('user')
        if user_info is None:
            raise Exception("Authentication required!")
        user_id = user_info.get('preferred_username')

        todo = ToDoItemModel(
            title=title,
            description=description,
            time=time,
            image_url=image_url,
            user_id=user_id
        )
        db_session.add(todo)
        db_session.commit()
        return CreateToDoItem(todo=todo)

class DeleteToDoItem(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user_info = info.context.get('user')
        if user_info is None:
            raise Exception("Authentication required!")
        user_id = user_info.get('preferred_username')

        # Decode the global ID
        type_name, id = from_global_id(id)
        id = int(id)

        todo = ToDoItemModel.query.filter_by(id=id, user_id=user_id).first()
        if not todo:
            raise Exception("ToDo item not found or not authorized to delete")

        db_session.delete(todo)
        db_session.commit()
        return DeleteToDoItem(success=True)


class UpdateToDoItem(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        time = graphene.DateTime()
        image_url = graphene.String()

    todo = graphene.Field(lambda: ToDoItem)

    def mutate(self, info, id, title=None, description=None, time=None, image_url=None):
        user_info = info.context.get('user')
        if user_info is None:
            raise Exception("Authentication required!")
        user_id = user_info.get('preferred_username')

        # Decode the global ID
        type_name, id = from_global_id(id)
        id = int(id)

        todo = ToDoItemModel.query.filter_by(id=id, user_id=user_id).first()
        if not todo:
            raise Exception("ToDo item not found or not authorized to update")

        if title:
            todo.title = title
        if description:
            todo.description = description
        if time:
            todo.time = time
        if image_url:
            todo.image_url = image_url

        db_session.commit()
        return UpdateToDoItem(todo=todo)

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_todos = SQLAlchemyConnectionField(ToDoItem)

    def resolve_all_todos(self, info, **kwargs):
        user_info = info.context.get('user')
        if user_info is None:
            raise Exception("Authentication required!")
        user_id = user_info.get('preferred_username')
        query = ToDoItem.get_query(info)
        return query.filter(ToDoItemModel.user_id == user_id)

class Mutation(graphene.ObjectType):
    create_todo = CreateToDoItem.Field()
    delete_todo = DeleteToDoItem.Field()
    update_todo = UpdateToDoItem.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
