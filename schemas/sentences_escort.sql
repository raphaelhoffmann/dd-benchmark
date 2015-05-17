-- Sentences table
DROP TABLE IF EXISTS sentences_escort CASCADE;
CREATE TABLE sentences_escort (
	doc_id text,
	sent_id int,
	text text,
	words text[],
        lemmas text[],
	poses text[],
	ners text[],
        offsets int[],
	dep_paths text[],
	dep_parents int[]
) DISTRIBUTED BY (doc_id);
