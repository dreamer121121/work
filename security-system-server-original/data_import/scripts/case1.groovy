import com.thinkaurelius.titan.core.TitanFactory;
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
graph = TitanFactory.open('conf/gremlin-server/titan-cassandra-es-server-case1.properties');
mgmt = graph.openManagement();
            
PropertyKey province = mgmt.containsPropertyKey("province") == false ? mgmt.makePropertyKey("province").dataType(String.class).make():mgmt.getPropertyKey("province");
PropertyKey INDEX = mgmt.containsPropertyKey("INDEX") == false ? mgmt.makePropertyKey("INDEX").dataType(String.class).make():mgmt.getPropertyKey("INDEX");
PropertyKey packages = mgmt.containsPropertyKey("packages") == false ? mgmt.makePropertyKey("packages").dataType(String.class).make():mgmt.getPropertyKey("packages");
PropertyKey hash = mgmt.containsPropertyKey("hash") == false ? mgmt.makePropertyKey("hash").dataType(String.class).make():mgmt.getPropertyKey("hash");
PropertyKey name = mgmt.containsPropertyKey("name") == false ? mgmt.makePropertyKey("name").dataType(String.class).make():mgmt.getPropertyKey("name");
PropertyKey country = mgmt.containsPropertyKey("country") == false ? mgmt.makePropertyKey("country").dataType(String.class).make():mgmt.getPropertyKey("country");
PropertyKey srcPort = mgmt.containsPropertyKey("srcPort") == false ? mgmt.makePropertyKey("srcPort").dataType(Integer.class).make():mgmt.getPropertyKey("srcPort");
PropertyKey bytes = mgmt.containsPropertyKey("bytes") == false ? mgmt.makePropertyKey("bytes").dataType(String.class).make():mgmt.getPropertyKey("bytes");
PropertyKey info = mgmt.containsPropertyKey("info") == false ? mgmt.makePropertyKey("info").dataType(String.class).make():mgmt.getPropertyKey("info");
PropertyKey accessExit = mgmt.containsPropertyKey("accessExit") == false ? mgmt.makePropertyKey("accessExit").dataType(String.class).make():mgmt.getPropertyKey("accessExit");
PropertyKey returnValue = mgmt.containsPropertyKey("returnValue") == false ? mgmt.makePropertyKey("returnValue").dataType(String.class).make():mgmt.getPropertyKey("returnValue");
PropertyKey time = mgmt.containsPropertyKey("time") == false ? mgmt.makePropertyKey("time").dataType(String.class).make():mgmt.getPropertyKey("time");
PropertyKey device = mgmt.containsPropertyKey("device") == false ? mgmt.makePropertyKey("device").dataType(String.class).make():mgmt.getPropertyKey("device");
PropertyKey tcpFlag = mgmt.containsPropertyKey("tcpFlag") == false ? mgmt.makePropertyKey("tcpFlag").dataType(String.class).make():mgmt.getPropertyKey("tcpFlag");
PropertyKey transProto = mgmt.containsPropertyKey("transProto") == false ? mgmt.makePropertyKey("transProto").dataType(String.class).make():mgmt.getPropertyKey("transProto");
PropertyKey dstPort = mgmt.containsPropertyKey("dstPort") == false ? mgmt.makePropertyKey("dstPort").dataType(Integer.class).make():mgmt.getPropertyKey("dstPort");
PropertyKey event = mgmt.containsPropertyKey("event") == false ? mgmt.makePropertyKey("event").dataType(String.class).make():mgmt.getPropertyKey("event");
if(!mgmt.containsVertexLabel("v_ip")){mgmt.makeVertexLabel("v_ip").make();}
if(!mgmt.containsVertexLabel("v_domain")){mgmt.makeVertexLabel("v_domain").make();}
if(!mgmt.containsVertexLabel("v_url")){mgmt.makeVertexLabel("v_url").make();}
if(!mgmt.containsEdgeLabel("e_attack")){mgmt.makeEdgeLabel('e_attack').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_access")){mgmt.makeEdgeLabel('e_access').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_ip2domain")){mgmt.makeEdgeLabel('e_ip2domain').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_ip2url")){mgmt.makeEdgeLabel('e_ip2url').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_domain2url")){mgmt.makeEdgeLabel('e_domain2url').multiplicity(Multiplicity.MULTI).make();}

mgmt.commit()
graph.tx().commit()

//bulid index
mgmt = graph.openManagement()
mgmt.buildIndex('index_v_all_byName_mixed', Vertex.class).addKey(mgmt.getPropertyKey('name'), Mapping.TEXTSTRING.asParameter()).buildMixedIndex("search")
mgmt.buildIndex('index_v_all_byName_composite', Vertex.class).addKey(mgmt.getPropertyKey('name')).buildCompositeIndex()
mgmt.buildIndex('index_e_all_byIndex_composite', Edge.class).addKey(mgmt.getPropertyKey('INDEX')).buildCompositeIndex()
mgmt.commit()

//await index registered
graph.tx().rollback()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_mixed').status(SchemaStatus.REGISTERED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_composite').status(SchemaStatus.REGISTERED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_e_all_byIndex_composite').status(SchemaStatus.REGISTERED).call()

//re index
mgmt = graph.openManagement()
mgmt.updateIndex(mgmt.getGraphIndex('index_v_all_byName_mixed'), SchemaAction.ENABLE_INDEX)
mgmt.updateIndex(mgmt.getGraphIndex('index_v_all_byName_composite'), SchemaAction.ENABLE_INDEX)
mgmt.updateIndex(mgmt.getGraphIndex('index_e_all_byIndex_composite'), SchemaAction.ENABLE_INDEX)
mgmt.commit()

//await index enabled
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_mixed').status(SchemaStatus.ENABLED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_composite').status(SchemaStatus.ENABLED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_e_all_byIndex_composite').status(SchemaStatus.ENABLED).call()

println 'success'
graph.close()