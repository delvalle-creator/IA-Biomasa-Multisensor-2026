<!DOCTYPE qgis>
<qgis version="3.28" styleCategories="Symbology">
  <renderer-v2 type="graduatedSymbol" attr="h_canopy_m" graduatedMethod="GraduatedColor">
    <ranges>
      <range lower="0" upper="5" label="0 - 5 m" symbol="0"/>
      <range lower="5" upper="10" label="5 - 10 m" symbol="1"/>
      <range lower="10" upper="20" label="10 - 20 m" symbol="2"/>
      <range lower="20" upper="35" label="20 - 35 m" symbol="3"/>
      <range lower="35" upper="200" label="mas de 35 m (revisar)" symbol="4"/>
    </ranges>
    <symbols>
      <symbol type="marker" name="0"><layer class="SimpleMarker">
        <prop k="color" v="237,248,233,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="1"><layer class="SimpleMarker">
        <prop k="color" v="186,228,179,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="2"><layer class="SimpleMarker">
        <prop k="color" v="116,196,118,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="3"><layer class="SimpleMarker">
        <prop k="color" v="44,95,45,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="4"><layer class="SimpleMarker">
        <prop k="color" v="238,0,0,255"/><prop k="size" v="2.2"/>
        <prop k="outline_style" v="no"/></layer></symbol>
    </symbols>
  </renderer-v2>
</qgis>
