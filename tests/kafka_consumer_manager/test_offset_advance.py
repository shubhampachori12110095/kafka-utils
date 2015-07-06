import contextlib
import mock
import pytest

from kafka_consumer_manager.commands.offset_advance import OffsetAdvance


@mock.patch('kafka_consumer_manager.commands.offset_advance.KafkaClient')
class TestOffsetAdvance(object):
    topics_partitions = {
        "topic1": [0, 1, 2],
        "topic2": [0, 1]
    }

    def test_run(self, mock_client):
        with contextlib.nested(
            mock.patch(
                "kafka_consumer_manager.commands.offset_manager.OffsetWriter."
                "preprocess_args",
                return_value=self.topics_partitions,
            ),
            mock.patch(
               "kafka_consumer_manager.commands.offset_advance.advance_consumer_offsets",
                autospec=True
            )
        ) as (mock_writer_process_args, mock_advance):
            args = mock.Mock(
                groupid="some_group",
                topic=None,
                partitions=None
            )
            cluster_config = mock.Mock()
            OffsetAdvance.run(args, cluster_config)

            ordered_args, _ = mock_advance.call_args
            assert ordered_args[1] == args.groupid
            assert ordered_args[2] == self.topics_partitions
            mock_client.return_value.load_metadata_for_topics.assert_called_once_with()
            mock_client.return_value.close.assert_called_once_with()

    def test_run_type_error(self, mock_client):
        with mock.patch(
            "kafka_consumer_manager.commands.offset_manager.OffsetWriter."
            "preprocess_args",
            return_value="some_string"
        ) as mock_writer_process_args:
            args = mock.Mock(
                groupid="some_group",
                topic=None,
                partitions=None
            )
            cluster_config = mock.Mock()
            with pytest.raises(TypeError):
                OffsetAdvance.run(args, cluster_config)
