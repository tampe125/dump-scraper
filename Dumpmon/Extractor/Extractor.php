<?php

namespace Dumpmon\Extractor;

abstract class Extractor
{
    /** @var  string    Data that will be analyzed */
    protected $data;

    /** @var  string    Extracted data from the file */
    protected $extracted;

    /**
     * Resets all the internal pointers
     */
    public function reset()
    {
        $this->extracted = '';
        $this->data      = '';
    }

    /**
     * Shorthand method to set all the features to the class
     *
     * @param array $features
     */
    public function setInfo(array $features = array())
    {
        foreach($features as $feature => $value)
        {
            if(property_exists($this, $feature))
            {
                $this->$feature = $value;
            }
        }
    }

    public function getExtractedData()
    {
        return $this->extracted;
    }

    /**
     * Entry point for analyzing the file
     *
     * @return void
     */
    public abstract function analyze();
}