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
graph = TitanFactory.open('conf/gremlin-server/titan-cassandra-es-server-knowledgeBase.properties');
mgmt = graph.openManagement();
            
PropertyKey INDEX = mgmt.containsPropertyKey("INDEX") == false ? mgmt.makePropertyKey("INDEX").dataType(String.class).make():mgmt.getPropertyKey("INDEX");
PropertyKey app = mgmt.containsPropertyKey("app") == false ? mgmt.makePropertyKey("app").dataType(String.class).make():mgmt.getPropertyKey("app");
PropertyKey extrainfo = mgmt.containsPropertyKey("extrainfo") == false ? mgmt.makePropertyKey("extrainfo").dataType(String.class).make():mgmt.getPropertyKey("extrainfo");
PropertyKey continent = mgmt.containsPropertyKey("continent") == false ? mgmt.makePropertyKey("continent").dataType(String.class).make():mgmt.getPropertyKey("continent");
PropertyKey city = mgmt.containsPropertyKey("city") == false ? mgmt.makePropertyKey("city").dataType(String.class).make():mgmt.getPropertyKey("city");
PropertyKey service = mgmt.containsPropertyKey("service") == false ? mgmt.makePropertyKey("service").dataType(String.class).make():mgmt.getPropertyKey("service");
PropertyKey mitigation = mgmt.containsPropertyKey("mitigation") == false ? mgmt.makePropertyKey("mitigation").dataType(String.class).make():mgmt.getPropertyKey("mitigation");
PropertyKey hostname = mgmt.containsPropertyKey("hostname") == false ? mgmt.makePropertyKey("hostname").dataType(String.class).make():mgmt.getPropertyKey("hostname");
PropertyKey lon = mgmt.containsPropertyKey("lon") == false ? mgmt.makePropertyKey("lon").dataType(String.class).make():mgmt.getPropertyKey("lon");
PropertyKey port = mgmt.containsPropertyKey("port") == false ? mgmt.makePropertyKey("port").dataType(String.class).make():mgmt.getPropertyKey("port");
PropertyKey version = mgmt.containsPropertyKey("version") == false ? mgmt.makePropertyKey("version").dataType(String.class).make():mgmt.getPropertyKey("version");
PropertyKey provider = mgmt.containsPropertyKey("provider") == false ? mgmt.makePropertyKey("provider").dataType(String.class).make():mgmt.getPropertyKey("provider");
PropertyKey hash = mgmt.containsPropertyKey("hash") == false ? mgmt.makePropertyKey("hash").dataType(String.class).make():mgmt.getPropertyKey("hash");
PropertyKey description = mgmt.containsPropertyKey("description") == false ? mgmt.makePropertyKey("description").dataType(String.class).make():mgmt.getPropertyKey("description");
PropertyKey timestamp = mgmt.containsPropertyKey("timestamp") == false ? mgmt.makePropertyKey("timestamp").dataType(String.class).make():mgmt.getPropertyKey("timestamp");
PropertyKey lat = mgmt.containsPropertyKey("lat") == false ? mgmt.makePropertyKey("lat").dataType(String.class).make():mgmt.getPropertyKey("lat");
PropertyKey banner = mgmt.containsPropertyKey("banner") == false ? mgmt.makePropertyKey("banner").dataType(String.class).make():mgmt.getPropertyKey("banner");
PropertyKey asn = mgmt.containsPropertyKey("asn") == false ? mgmt.makePropertyKey("asn").dataType(String.class).make():mgmt.getPropertyKey("asn");
PropertyKey name = mgmt.containsPropertyKey("name") == false ? mgmt.makePropertyKey("name").dataType(String.class).make():mgmt.getPropertyKey("name");
PropertyKey level = mgmt.containsPropertyKey("level") == false ? mgmt.makePropertyKey("level").dataType(String.class).make():mgmt.getPropertyKey("level");
PropertyKey url = mgmt.containsPropertyKey("url") == false ? mgmt.makePropertyKey("url").dataType(String.class).make():mgmt.getPropertyKey("url");
PropertyKey country = mgmt.containsPropertyKey("country") == false ? mgmt.makePropertyKey("country").dataType(String.class).make():mgmt.getPropertyKey("country");
PropertyKey time = mgmt.containsPropertyKey("time") == false ? mgmt.makePropertyKey("time").dataType(String.class).make():mgmt.getPropertyKey("time");
PropertyKey os = mgmt.containsPropertyKey("os") == false ? mgmt.makePropertyKey("os").dataType(String.class).make():mgmt.getPropertyKey("os");
if(!mgmt.containsVertexLabel("v_protocol")){mgmt.makeVertexLabel("v_protocol").make();}
if(!mgmt.containsVertexLabel("v_deviceType")){mgmt.makeVertexLabel("v_deviceType").make();}
if(!mgmt.containsVertexLabel("v_device")){mgmt.makeVertexLabel("v_device").make();}
if(!mgmt.containsVertexLabel("v_instance")){mgmt.makeVertexLabel("v_instance").make();}
if(!mgmt.containsVertexLabel("v_vendor")){mgmt.makeVertexLabel("v_vendor").make();}
if(!mgmt.containsVertexLabel("v_event")){mgmt.makeVertexLabel("v_event").make();}
if(!mgmt.containsVertexLabel("v_vulnerability")){mgmt.makeVertexLabel("v_vulnerability").make();}
if(!mgmt.containsEdgeLabel("e_devType2dev")){mgmt.makeEdgeLabel('e_devType2dev').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_dev2vendor")){mgmt.makeEdgeLabel('e_dev2vendor').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_ins2ven")){mgmt.makeEdgeLabel('e_ins2ven').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_vul2ven")){mgmt.makeEdgeLabel('e_vul2ven').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_ins2pro")){mgmt.makeEdgeLabel('e_ins2pro').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_dev2vendor")){mgmt.makeEdgeLabel('e_dev2vendor').multiplicity(Multiplicity.MULTI).make();}

mgmt.commit()
graph.tx().commit()

//bulid index
mgmt = graph.openManagement()
mgmt.buildIndex('index_v_all_byName_composite', Vertex.class).addKey(mgmt.getPropertyKey('name')).buildCompositeIndex()
mgmt.buildIndex('index_v_all_byName_mixed', Vertex.class).addKey(mgmt.getPropertyKey('name'), Mapping.TEXTSTRING.asParameter()).buildMixedIndex("search")
mgmt.buildIndex('index_e_all_byIndex_mixed', Edge.class).addKey(mgmt.getPropertyKey('INDEX'), Mapping.TEXTSTRING.asParameter()).buildMixedIndex("search")
mgmt.buildIndex('index_e_all_byIndex_composite', Edge.class).addKey(mgmt.getPropertyKey('INDEX')).buildCompositeIndex()
mgmt.commit()

//await index registered
graph.tx().rollback()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_composite').status(SchemaStatus.REGISTERED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_mixed').status(SchemaStatus.REGISTERED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_e_all_byIndex_mixed').status(SchemaStatus.REGISTERED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_e_all_byIndex_composite').status(SchemaStatus.REGISTERED).call()

//re index
mgmt = graph.openManagement()
mgmt.updateIndex(mgmt.getGraphIndex('index_v_all_byName_composite'), SchemaAction.ENABLE_INDEX)
mgmt.updateIndex(mgmt.getGraphIndex('index_v_all_byName_mixed'), SchemaAction.ENABLE_INDEX)
mgmt.updateIndex(mgmt.getGraphIndex('index_e_all_byIndex_mixed'), SchemaAction.ENABLE_INDEX)
mgmt.updateIndex(mgmt.getGraphIndex('index_e_all_byIndex_composite'), SchemaAction.ENABLE_INDEX)
mgmt.commit()

//await index enabled
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_composite').status(SchemaStatus.ENABLED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_v_all_byName_mixed').status(SchemaStatus.ENABLED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_e_all_byIndex_mixed').status(SchemaStatus.ENABLED).call()
ManagementSystem.awaitGraphIndexStatus(graph, 'index_e_all_byIndex_composite').status(SchemaStatus.ENABLED).call()

println 'success'
graph.close()