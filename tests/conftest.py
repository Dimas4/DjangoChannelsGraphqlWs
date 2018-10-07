#
# coding: utf-8
# Copyright (c) 2018 DATADVANCE
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Auxiliary fixtures to simplify testing."""

import channels
import django
import graphene
import pytest

import channels_graphql_ws
import channels_graphql_ws.testing


@pytest.fixture
def gql():
    """PyTest fixture for testing GraphQL WebSocket backends.

    The fixture provides a method to setup GraphQL testing backend for
    the given GraphQL schema (query, mutation, and subscription). In
    particular: it sets up an instance of `GraphqlWsConsumer` and an
    instance of `GraphqlWsCommunicator`. The former one is returned from
    the function.

    Syntax:
        gql(
            *,
            query=None,
            mutation=None,
            subscription=None,
            consumer_attrs=None,
            communicator_kwds=None
        ):

    Args:
        query: Root GraphQL query. Optional.
        mutation: Root GraphQL subscription. Optional.
        subscription: Root GraphQL mutation. Optional.
        consumer_attrs: `GraphqlWsConsumer` attributes dict. Optional.
        communicator_kwds: Extra keyword arguments for the Channels
            `channels.testing.WebsocketCommunicator`. Optional.

    Returns:
        An instance of the `GraphqlWsCommunicator` class which has many
        useful GraphQL-related methods, see the `GraphqlWsCommunicator`
        class docstrings for details.

    Use like this:
    ```
    def test_something(gql):
        comm = gql(
            # GraphQl schema.
            query=MyQuery,
            mutation=MyMutation,
            subscription=MySubscription,
            # `GraphqlWsConsumer` settings.
            consumer_attrs={"strict_ordering": True},
            # `channels.testing.WebsocketCommunicator` settings.
            communicator_kwds={"headers": [...]}
        )
        ...
    ```

    """

    def communicator_constructor(
        *,
        query=None,
        mutation=None,
        subscription=None,
        consumer_attrs=None,
        communicator_kwds=None,
    ):
        """Setup GraphQL consumer and the communicator for tests."""

        class ChannelsConsumer(channels_graphql_ws.GraphqlWsConsumer):
            """Channels WebSocket consumer for GraphQL API."""

            schema = graphene.Schema(
                query=query,
                mutation=mutation,
                subscription=subscription,
                auto_camelcase=False,
            )

        # Set additional attributes to the `ChannelsConsumer`.
        if consumer_attrs is not None:
            for attr, val in consumer_attrs.items():
                setattr(ChannelsConsumer, attr, val)

        application = channels.routing.ProtocolTypeRouter(
            {
                "websocket": channels.routing.URLRouter(
                    [django.urls.path("graphql/", ChannelsConsumer)]
                )
            }
        )

        graphql_ws_communicator = channels_graphql_ws.testing.GraphqlWsCommunicator(
            application=application, path="graphql/", **(communicator_kwds or {})
        )

        return graphql_ws_communicator

    return communicator_constructor
