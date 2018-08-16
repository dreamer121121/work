#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import sys


class SchemaBuild():
    def __init__(self, filePath):
        self.JSON = json.load(file(filePath))
        self.JSON["schema"] = file(filePath).name.split('.')[0]

    def write_head(self):
        fileHandler = file(self.JSON["schema"] + ".groovy", 'w')
        fileHandler.write("""import com.thinkaurelius.titan.core.TitanFactory;
import com.thinkaurelius.titan.core.TitanTransaction;
import com.thinkaurelius.titan.core.EdgeLabel;
import com.thinkaurelius.titan.core.Multiplicity;
import com.thinkaurelius.titan.core.PropertyKey;
import com.thinkaurelius.titan.core.schema.TitanGraphIndex;
import com.thinkaurelius.titan.core.schema.TitanManagement;
import org.apache.tinkerpop.gremlin.structure.Edge;
import org.apache.tinkerpop.gremlin.structure.T;
import org.apache.tinkerpop.gremlin.structure.Vertex;
import com.thinkaurelius.titan.core.schema.SchemaAction;
import com.thinkaurelius.titan.core.schema.ConsistencyModifier;
import com.thinkaurelius.titan.core.schema.Mapping;
import com.thinkaurelius.titan.graphdb.database.management.ManagementSystem;
import com.thinkaurelius.titan.core.schema.SchemaStatus;
graph = TitanFactory.open('conf/gremlin-server/titan-cassandra-es-server-%s.properties');
mgmt = graph.openManagement();
            """ % self.JSON["schema"])

    def write_content(self):
        fileHandler = file(self.JSON["schema"] + ".groovy", 'a+')

        for key, dataType in self.JSON["properties"].items():
            fileHandler.write(
                "\nPropertyKey %s = mgmt.containsPropertyKey(\"%s\") == false ? mgmt.makePropertyKey(\"%s\").dataType(%s.class).make():mgmt.getPropertyKey(\"%s\");" % (
                key, key, key, dataType, key))
        for vertex in self.JSON["vertices"]:
            type = "v_" + vertex["type"]
            fileHandler.write(
                "\nif(!mgmt.containsVertexLabel(\"%s\")){mgmt.makeVertexLabel(\"%s\").make();}" % (type, type))

        for edge in self.JSON["edges"]:
            type = "e_" + edge["type"]
            print(type)
            fileHandler.write(
                "\nif(!mgmt.containsEdgeLabel(\"%s\")){mgmt.makeEdgeLabel('%s').multiplicity(Multiplicity.%s).make();}" % (
                type, type, edge["multiplicity"]))

        fileHandler.write("\n\nmgmt.commit()\ngraph.tx().commit()\n\n")

        # ------------build index----------------#

        buildIndex = "//bulid index\nmgmt = graph.openManagement()\n"
        awaitRegis = "//await index registered\ngraph.tx().rollback()\n"
        reIndex = "//re index\nmgmt = graph.openManagement()\n"
        awaitEnable = "//await index enabled\n"

        for index in self.JSON["index"]:
            indexType = index["index_type"]
            indexKey = ""
            keyCount = 0
            for property in index["properties"]:
                if keyCount > 0:
                    indexKey += "And"
                indexKey += property.capitalize()
                keyCount += 1
            indexKey = "index_%s_%s_by%s_%s" % (
            index["v_or_e"], index.get("type", "all"), indexKey, index["index_type"])

            VE = ""
            if index["v_or_e"] == "v":
                VE = "Vertex"
            elif index["v_or_e"] == "e":
                VE = "Edge"
            buildIndex += "mgmt.buildIndex('%s', %s.class)" % (indexKey, VE)

            for property in index["properties"]:
                buildIndex += ".addKey(mgmt.getPropertyKey('%s')" % property
                if indexType == "composite":
                    buildIndex += ")"
                elif indexType == "mixed":
                    buildIndex += ", Mapping.TEXTSTRING.asParameter())"

            if index.get("unique", "false") == "true":
                buildIndex += ".unique()"
            if index.get("type", "all") != "all":
                buildIndex += ".indexOnly(mgmt.get%sLabel('%s_%s'))" % (VE, index["v_or_e"], index["type"])

            if indexType == "composite":
                buildIndex += ".buildCompositeIndex()"
            elif indexType == "mixed":
                buildIndex += ".buildMixedIndex(\"search\")"
            buildIndex += "\n"

            awaitRegis += "ManagementSystem.awaitGraphIndexStatus(graph, '%s').status(SchemaStatus.REGISTERED).call()\n" % indexKey
            reIndex += "mgmt.updateIndex(mgmt.getGraphIndex('%s'), SchemaAction.ENABLE_INDEX)\n" % indexKey
            awaitEnable += "ManagementSystem.awaitGraphIndexStatus(graph, '%s').status(SchemaStatus.ENABLED).call()\n" % indexKey

        buildIndex += "mgmt.commit()\n\n"
        awaitRegis += "\n"
        reIndex += "mgmt.commit()\n\n"
        awaitEnable += "\n"

        fileHandler.write(buildIndex + awaitRegis + reIndex + awaitEnable + "println 'success'\n" + "graph.close()")
        fileHandler.close
        return


def main():
    if len(sys.argv) == 2:
        hello = SchemaBuild(sys.argv[1])
        hello.write_head()
        hello.write_content()


if __name__ == '__main__':
    main()
