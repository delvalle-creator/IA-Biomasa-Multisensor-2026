<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">
  <!-- Altura del dosel predicha (m)
       ADVERTENCIA: el modelo de altura subestima los arboles altos (sesgo medido
       de casi 10 m por encima de 15 m) y la alometria lo amplifica. Este mapa
       SUBESTIMA los rodales altos. Ver TP5_03 y TP5_04. -->
  <pipe><rasterrenderer type="singlebandpseudocolor" band="1" opacity="1">
    <rastershader><colorrampshader classificationMode="1" colorRampType="INTERPOLATED">
      <item value="0" color="#f7fcf5" label="0 m"/>
      <item value="5" color="#a1d99b" label="5 m"/>
      <item value="15" color="#41ab5d" label="15 m"/>
      <item value="30" color="#00441b" label="30 m"/>
    </colorrampshader></rastershader>
  </rasterrenderer></pipe>
</qgis>
