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
graph = TitanFactory.open('conf/gremlin-server/titan-cassandra-es-server-case2.properties');
mgmt = graph.openManagement();
            
PropertyKey INDEX = mgmt.containsPropertyKey("INDEX") == false ? mgmt.makePropertyKey("INDEX").dataType(String.class).make():mgmt.getPropertyKey("INDEX");
PropertyKey tcpFlag = mgmt.containsPropertyKey("tcpFlag") == false ? mgmt.makePropertyKey("tcpFlag").dataType(String.class).make():mgmt.getPropertyKey("tcpFlag");
PropertyKey RPReqType = mgmt.containsPropertyKey("RPReqType") == false ? mgmt.makePropertyKey("RPReqType").dataType(String.class).make():mgmt.getPropertyKey("RPReqType");
PropertyKey srcPort = mgmt.containsPropertyKey("srcPort") == false ? mgmt.makePropertyKey("srcPort").dataType(Integer.class).make():mgmt.getPropertyKey("srcPort");
PropertyKey direct = mgmt.containsPropertyKey("direct") == false ? mgmt.makePropertyKey("direct").dataType(String.class).make():mgmt.getPropertyKey("direct");
PropertyKey respVal = mgmt.containsPropertyKey("respVal") == false ? mgmt.makePropertyKey("respVal").dataType(String.class).make():mgmt.getPropertyKey("respVal");
PropertyKey returnValue = mgmt.containsPropertyKey("returnValue") == false ? mgmt.makePropertyKey("returnValue").dataType(String.class).make():mgmt.getPropertyKey("returnValue");
PropertyKey dstPort = mgmt.containsPropertyKey("dstPort") == false ? mgmt.makePropertyKey("dstPort").dataType(Integer.class).make():mgmt.getPropertyKey("dstPort");
PropertyKey TTL = mgmt.containsPropertyKey("TTL") == false ? mgmt.makePropertyKey("TTL").dataType(String.class).make():mgmt.getPropertyKey("TTL");
PropertyKey province = mgmt.containsPropertyKey("province") == false ? mgmt.makePropertyKey("province").dataType(String.class).make():mgmt.getPropertyKey("province");
PropertyKey hash = mgmt.containsPropertyKey("hash") == false ? mgmt.makePropertyKey("hash").dataType(String.class).make():mgmt.getPropertyKey("hash");
PropertyKey DNSServer = mgmt.containsPropertyKey("DNSServer") == false ? mgmt.makePropertyKey("DNSServer").dataType(String.class).make():mgmt.getPropertyKey("DNSServer");
PropertyKey DSU = mgmt.containsPropertyKey("DSU") == false ? mgmt.makePropertyKey("DSU").dataType(String.class).make():mgmt.getPropertyKey("DSU");
PropertyKey reqCount = mgmt.containsPropertyKey("reqCount") == false ? mgmt.makePropertyKey("reqCount").dataType(String.class).make():mgmt.getPropertyKey("reqCount");
PropertyKey DSI = mgmt.containsPropertyKey("DSI") == false ? mgmt.makePropertyKey("DSI").dataType(String.class).make():mgmt.getPropertyKey("DSI");
PropertyKey transProto = mgmt.containsPropertyKey("transProto") == false ? mgmt.makePropertyKey("transProto").dataType(String.class).make():mgmt.getPropertyKey("transProto");
PropertyKey packages = mgmt.containsPropertyKey("packages") == false ? mgmt.makePropertyKey("packages").dataType(String.class).make():mgmt.getPropertyKey("packages");
PropertyKey reqDomain = mgmt.containsPropertyKey("reqDomain") == false ? mgmt.makePropertyKey("reqDomain").dataType(String.class).make():mgmt.getPropertyKey("reqDomain");
PropertyKey info = mgmt.containsPropertyKey("info") == false ? mgmt.makePropertyKey("info").dataType(String.class).make():mgmt.getPropertyKey("info");
PropertyKey respFlag = mgmt.containsPropertyKey("respFlag") == false ? mgmt.makePropertyKey("respFlag").dataType(String.class).make():mgmt.getPropertyKey("respFlag");
PropertyKey name = mgmt.containsPropertyKey("name") == false ? mgmt.makePropertyKey("name").dataType(String.class).make():mgmt.getPropertyKey("name");
PropertyKey RSIP = mgmt.containsPropertyKey("RSIP") == false ? mgmt.makePropertyKey("RSIP").dataType(String.class).make():mgmt.getPropertyKey("RSIP");
PropertyKey SR = mgmt.containsPropertyKey("SR") == false ? mgmt.makePropertyKey("SR").dataType(String.class).make():mgmt.getPropertyKey("SR");
PropertyKey country = mgmt.containsPropertyKey("country") == false ? mgmt.makePropertyKey("country").dataType(String.class).make():mgmt.getPropertyKey("country");
PropertyKey bytes = mgmt.containsPropertyKey("bytes") == false ? mgmt.makePropertyKey("bytes").dataType(String.class).make():mgmt.getPropertyKey("bytes");
PropertyKey time = mgmt.containsPropertyKey("time") == false ? mgmt.makePropertyKey("time").dataType(String.class).make():mgmt.getPropertyKey("time");
PropertyKey reqType = mgmt.containsPropertyKey("reqType") == false ? mgmt.makePropertyKey("reqType").dataType(String.class).make():mgmt.getPropertyKey("reqType");
if(!mgmt.containsVertexLabel("v_ip")){mgmt.makeVertexLabel("v_ip").make();}
if(!mgmt.containsVertexLabel("v_department")){mgmt.makeVertexLabel("v_department").make();}
if(!mgmt.containsVertexLabel("v_file")){mgmt.makeVertexLabel("v_file").make();}
if(!mgmt.containsVertexLabel("v_url")){mgmt.makeVertexLabel("v_url").make();}
if(!mgmt.containsVertexLabel("v_domain")){mgmt.makeVertexLabel("v_domain").make();}
if(!mgmt.containsEdgeLabel("e_ip2dep")){mgmt.makeEdgeLabel('e_ip2dep').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_ip2file")){mgmt.makeEdgeLabel('e_ip2file').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_url2file")){mgmt.makeEdgeLabel('e_url2file').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_ip2url")){mgmt.makeEdgeLabel('e_ip2url').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_DNS")){mgmt.makeEdgeLabel('e_DNS').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_ip2domain")){mgmt.makeEdgeLabel('e_ip2domain').multiplicity(Multiplicity.MULTI).make();}
if(!mgmt.containsEdgeLabel("e_access")){mgmt.makeEdgeLabel('e_access').multiplicity(Multiplicity.MULTI).make();}

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